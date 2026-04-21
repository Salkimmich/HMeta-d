(ns hmeta-d.sampler
  (:require [fastmath.random :as r]))

;; MATLAB: type-2 likelihood equations live inside fit_meta_d_mcmc.m / JAGS model.
;; Python:  phase2_sampler.py makes them explicit functions over dict parameters.
;; Clojure: this namespace keeps the same pieces as pure map/vector transformations.

(defn- build-t2-criteria
  [c1 c2 nratings]
  (when (not= (count c2) (dec nratings))
    (throw (ex-info "c2 must have length nratings - 1" {:nratings nratings :c2-count (count c2)})))
  (let [left  (mapv #(- c1 %) (reverse c2))
        right (mapv #(+ c1 %) c2)]
    (vec (concat left right))))

(defn estimate-type2-rates
  "MATLAB: 'find estimated t2FAR and t2HR' loop in fit_meta_d_mcmc.m.
   Python: estimate_type2_rates builds predicted type-2 ROC rates.
   Clojure: return four vectors in a plain map keyed by response side."
  [meta-d c1 c2 nratings]
  (let [s1-mu (/ (- meta-d) 2.0)
        s2-mu (/ meta-d 2.0)
        cdf (fn [x mu sd] (r/cdf (r/distribution :normal {:mu mu :sd sd}) x))
        c-area-rs2 (- 1.0 (cdf c1 s2-mu 1.0))
        i-area-rs2 (- 1.0 (cdf c1 s1-mu 1.0))
        c-area-rs1 (cdf c1 s1-mu 1.0)
        i-area-rs1 (cdf c1 s2-mu 1.0)
        t2c1 (build-t2-criteria c1 c2 nratings)]
    (if (<= (min c-area-rs2 i-area-rs2 c-area-rs1 i-area-rs1) 0.0)
      {:far-s1 [] :hr-s1 [] :far-s2 [] :hr-s2 []}
      (reduce (fn [acc i]
                (let [lower (nth t2c1 (- nratings i 1))
                      upper (nth t2c1 (+ (- nratings 2) i))
                      i-far-area-rs2 (- 1.0 (cdf upper s1-mu 1.0))
                      c-hr-area-rs2 (- 1.0 (cdf upper s2-mu 1.0))
                      i-far-area-rs1 (cdf lower s2-mu 1.0)
                      c-hr-area-rs1 (cdf lower s1-mu 1.0)]
                  (-> acc
                      (update :far-s2 conj (/ i-far-area-rs2 i-area-rs2))
                      (update :hr-s2 conj (/ c-hr-area-rs2 c-area-rs2))
                      (update :far-s1 conj (/ i-far-area-rs1 i-area-rs1))
                      (update :hr-s1 conj (/ c-hr-area-rs1 c-area-rs1)))))
              {:far-s1 [] :hr-s1 [] :far-s2 [] :hr-s2 []}
              (range 1 nratings)))))

(defn- observed-type2-counts
  [data]
  (let [nratings (:nratings data)
        n (* 2 nratings)
        counts (:counts data)
        nR-S1 (subvec counts 0 n)
        nR-S2 (subvec counts n (* 2 n))
        i-nR-rS2 (subvec nR-S1 nratings n)
        c-nR-rS2 (subvec nR-S2 nratings n)
        i-nR-rS1 (vec (reverse (subvec nR-S2 0 nratings)))
        c-nR-rS1 (vec (reverse (subvec nR-S1 0 nratings)))
        idxs (range 1 nratings)
        cumul (fn [v i] (reduce + (subvec v i (count v))))]
    {:far-s2 {:k (mapv #(cumul i-nR-rS2 %) idxs) :n (reduce + i-nR-rS2)}
     :hr-s2  {:k (mapv #(cumul c-nR-rS2 %) idxs) :n (reduce + c-nR-rS2)}
     :far-s1 {:k (mapv #(cumul i-nR-rS1 %) idxs) :n (reduce + i-nR-rS1)}
     :hr-s1  {:k (mapv #(cumul c-nR-rS1 %) idxs) :n (reduce + c-nR-rS1)}}))

(defn- clamp-prob [p tol]
  (max tol (min (- 1.0 tol) p)))

(defn log-likelihood
  "MATLAB: JAGS computes this implicitly from model block.
   Python: log_likelihood explicitly scores params against observed counts.
   Clojure: compute binomial log-likelihood terms directly from maps."
  [params data]
  (let [meta-d (:meta-d params)
        c2 (vec (:c2 params))]
    (if (or (some #(<= % 0.0) c2)
            (not= (count c2) (dec (:nratings data))))
      ##-Inf
      (let [{:keys [far-s1 hr-s1 far-s2 hr-s2]}
            (estimate-type2-rates meta-d (:c1 data) c2 (:nratings data))
            obs (observed-type2-counts data)
            tol (:tol data)
            pred {:far-s1 (mapv #(clamp-prob % tol) far-s1)
                  :hr-s1  (mapv #(clamp-prob % tol) hr-s1)
                  :far-s2 (mapv #(clamp-prob % tol) far-s2)
                  :hr-s2  (mapv #(clamp-prob % tol) hr-s2)}
            binom-ll (fn [k n p]
                       (let [dist (r/distribution :binomial {:trials n :p p})]
                         (Math/log (max 1e-300 (r/pdf dist k)))))]
        (reduce (fn [acc key]
                  (let [ks (get-in obs [key :k])
                        n (get-in obs [key :n])
                        ps (get pred key)]
                    (+ acc (reduce + (map (fn [k p] (binom-ll k n p)) ks ps)))))
                0.0
                [:far-s1 :hr-s1 :far-s2 :hr-s2])))))

(defn- log-prior
  [params data]
  (let [meta-d (:meta-d params)
        c2 (:c2 params)
        normal-pdf (fn [x mu sd] (r/pdf (r/distribution :normal {:mu mu :sd sd}) x))
        meta-prior (Math/log (max 1e-300 (normal-pdf meta-d (:d1 data) 2.0)))
        c2-prior (reduce + (map #(Math/log (max 1e-300 (normal-pdf % 0.5 1.0))) c2))]
    (+ meta-prior c2-prior)))

(defn mh-chain
  "MATLAB: MCMC state evolution occurs in JAGS.
   Python: mh_chain loops proposals over parameter dicts.
   Clojure: explicit MH transition over immutable parameter maps."
  [init-params data-or-cfg step-size]
  (let [rng (r/rng :jdk 0)
        {:keys [n-samples n-burnin] :or {n-samples 1000 n-burnin 0}} (:mcmc data-or-cfg)
        log-post (if-let [lp (:log-posterior data-or-cfg)]
                   lp
                   (fn [p] (+ (log-prior p data-or-cfg) (log-likelihood p data-or-cfg))))
        draw-proposal (fn [params]
                        (reduce-kv (fn [m k v]
                                     (assoc m k
                                            (if (vector? v)
                                              (mapv #(+ % (r/grand rng step-size)) v)
                                              (+ v (r/grand rng step-size)))))
                                   {}
                                   params))
        total-iters (+ n-samples n-burnin)]
    (loop [iter 0
           current init-params
           current-lp (double (log-post init-params))
           out []]
      (if (= iter total-iters)
        out
        (let [proposal (draw-proposal current)
              proposal-lp (double (log-post proposal))
              accept? (and (Double/isFinite proposal-lp)
                           (< (Math/log (r/drand rng)) (- proposal-lp current-lp)))
              next-state (if accept? proposal current)
              next-lp (if accept? proposal-lp current-lp)
              out' (if (>= iter n-burnin) (conj out next-state) out)]
          (recur (inc iter) next-state next-lp out'))))))
