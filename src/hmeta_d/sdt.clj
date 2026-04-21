(ns hmeta-d.sdt
  (:require [fastmath.random :as r]))

;; MATLAB: pre-JAGS block in fit_meta_d_mcmc.m computes padded counts, cumulative
;;         rates, and then d1/c1 from inverse normal transforms.
;; Python:  phase1_sdt.py mirrors this with numpy/scipy.
;; Clojure: same computations as pure functions returning plain maps/vectors.

(defn pad-counts
  "Add smoothing used by the MATLAB implementation:
   adj_f = 1 / length(nR_S1) = 1 / (2 * nratings)."
  [counts nratings]
  (let [pad (/ 1.0 (* 2 nratings))]
    (mapv #(+ (double %) pad) counts)))

(defn compute-rates
  "Compute cumulative HR/FAR arrays and type-1 HR/FAR at t1 threshold.
   Mirrors MATLAB loop:
   for c = 2:nRatings*2
       ratingHR(end+1) = sum(nR_S2_adj(c:end))/sum(nR_S2_adj)
       ratingFAR(end+1) = sum(nR_S1_adj(c:end))/sum(nR_S1_adj)"
  [nR-S1 nR-S2]
  (when (not= (count nR-S1) (count nR-S2))
    (throw (ex-info "nR_S1 and nR_S2 must have same length" {})))
  (when (odd? (count nR-S1))
    (throw (ex-info "Input vectors must have an even number of elements" {})))
  (let [n (count nR-S1)
        nratings (/ n 2)
        nR-S1-adj (pad-counts nR-S1 nratings)
        nR-S2-adj (pad-counts nR-S2 nratings)
        total-s1 (reduce + nR-S1-adj)
        total-s2 (reduce + nR-S2-adj)
        idxs (range 1 n)
        rating-hr (mapv (fn [c] (/ (reduce + (subvec nR-S2-adj c n)) total-s2)) idxs)
        rating-far (mapv (fn [c] (/ (reduce + (subvec nR-S1-adj c n)) total-s1)) idxs)
        t1-index (dec nratings)]
    {:hit-rate   (nth rating-hr t1-index)
     :fa-rate    (nth rating-far t1-index)
     :rating-hr  rating-hr
     :rating-far rating-far}))

(defn normal-ppf
  "Inverse normal CDF; fastmath 2.4 public API."
  [p]
  (r/icdf r/default-normal p))

(defn compute-d1
  "Type-1 d-prime = norminv(HR) - norminv(FAR)."
  [hit-rate fa-rate]
  (- (normal-ppf hit-rate) (normal-ppf fa-rate)))

(defn compute-c1
  "Type-1 criterion = -0.5 * (norminv(HR) + norminv(FAR))."
  [hit-rate fa-rate]
  (* -0.5 (+ (normal-ppf hit-rate) (normal-ppf fa-rate))))

(defn prepare-sdt-data
  "MATLAB-equivalent SDT preparation for JAGS datastruct fields."
  [nR-S1 nR-S2]
  (when (not= (count nR-S1) (count nR-S2))
    (throw (ex-info "nR_S1 and nR_S2 must have same length" {})))
  (when (odd? (count nR-S1))
    (throw (ex-info "Input vectors must have an even number of elements" {})))
  (let [nratings (/ (count nR-S1) 2)
        {:keys [hit-rate fa-rate]} (compute-rates nR-S1 nR-S2)]
    {:d1       (double (compute-d1 hit-rate fa-rate))
     :c1       (double (compute-c1 hit-rate fa-rate))
     :counts   (vec (concat (mapv double nR-S1) (mapv double nR-S2)))
     :nratings nratings
     :nTot     (+ (reduce + nR-S1) (reduce + nR-S2))
     :tol      1e-5}))
