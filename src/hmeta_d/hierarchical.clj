(ns hmeta-d.hierarchical
  "Phase 3: Hierarchical model as plain data."
  (:import [java.util Random])
  (:require [fastmath.random :as r]
            [hmeta-d.sampler :as sampler]))

;; MATLAB: external JAGS .bugs file.
;; Python: dataclass model object.
;; Clojure: plain EDN map transformable with assoc-in.
(def hmeta-d-group-model
  {:priors
   {:mu-logMratio {:dist :normal :mu 0.0 :sigma 1.0 :truncated false}
    :sigma-logMratio {:dist :half-normal :mu 0.0 :sigma 1.0 :truncated true}
    :mu-c2 {:dist :normal :mu 0.0 :sigma 1.0 :truncated false}
    :sigma-c2 {:dist :half-normal :mu 0.0 :sigma 1.0 :truncated true}}
   :mcmc
   {:n-chains 3 :n-samples 1000 :n-burnin 200 :step-size 0.1 :seed 42}})

(def tighter-prior-model
  (assoc-in hmeta-d-group-model [:priors :sigma-logMratio :sigma] 0.5))

(defn prior-logpdf
  "MATLAB: prior line in JAGS block.
   Python: loop over dataclass prior fields.
   Clojure: dispatch by :dist in plain map."
  [{:keys [dist mu sigma truncated]} value]
  (cond
    (and truncated (< value 0.0)) ##-Inf
    (or (= dist :normal) (= dist :half-normal))
    (let [density (r/pdf (r/distribution :normal {:mu mu :sd sigma}) value)]
      (Math/log (max 1e-300 density)))
    :else
    (throw (ex-info "Unknown distribution" {:dist dist}))))

(defn log-prior-group
  "MATLAB: prior block in JAGS model.
   Python: log_prior_group over model fields.
   Clojure: reduce-kv over :priors map."
  [group-params model]
  (reduce-kv
   (fn [acc param-name prior-spec]
     (let [lp (prior-logpdf prior-spec (double (get group-params param-name 0.0)))]
       (if (= lp ##-Inf) (reduced ##-Inf) (+ acc lp))))
   0.0
   (:priors model)))

(defn group-log-likelihood
  "MATLAB: subject loop in group JAGS model.
   Python: group_log_likelihood explicit loop.
   Clojure: reduce over subject data with sampled subject latents."
  [group-params subject-data]
  (let [seed (long (get group-params :seed 0))
        rng (Random. seed)
        mu (:mu-logMratio group-params)
        sigma (:sigma-logMratio group-params)
        mu-c2 (:mu-c2 group-params)
        sigma-c2 (max 1e-6 (:sigma-c2 group-params))]
    (reduce
     (fn [acc data]
       (let [log-mratio (+ mu (* sigma (.nextGaussian rng)))
             mratio (Math/exp log-mratio)
             meta-d (* mratio (:d1 data))
             c2 (mapv (fn [_] (Math/abs (+ mu-c2 (* sigma-c2 (.nextGaussian rng)))))
                      (range (dec (:nratings data))))
             ll (sampler/log-likelihood {:meta-d meta-d :c2 c2} data)]
         (+ acc ll)))
     0.0
     subject-data)))

(defn fit-group
  "MATLAB: fit_meta_d_mcmc_group using JAGS.
   Python: fit_group uses model dataclass config.
   Clojure: use model map config and sampler/mh-chain."
  [model subject-data]
  (let [{:keys [n-chains n-samples n-burnin step-size seed]} (:mcmc model)
        log-post (fn [params]
                   (+ (log-prior-group params model)
                      (group-log-likelihood params subject-data)))]
    (->> (range n-chains)
         (mapv (fn [idx]
                 (sampler/mh-chain
                  {:mu-logMratio 0.0
                   :sigma-logMratio 0.5
                   :mu-c2 0.5
                   :sigma-c2 0.5
                   :seed (+ seed idx)}
                  {:log-posterior log-post
                   :mcmc {:n-samples n-samples :n-burnin n-burnin}}
                  step-size))))))
