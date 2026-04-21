(ns hmeta-d.hierarchical-test
  (:require [clojure.test :refer [deftest testing is]]
            [hmeta-d.hierarchical :as h]
            [hmeta-d.sdt :as sdt]))

(def subject-data
  [(sdt/prepare-sdt-data [36 24 17 20 10 12 34 22] [21 19 23 28 33 28 20 19])
   (sdt/prepare-sdt-data [30 20 18 22 12 10 36 24] [22 18 24 26 30 26 22 20])])

(deftest model-as-data-tests
  (testing "model is inspectable data"
    (is (contains? (:priors h/hmeta-d-group-model) :mu-logMratio))
    (is (= 1.0 (get-in h/hmeta-d-group-model [:priors :mu-logMratio :sigma]))))

  (testing "assoc-in non-destructive prior update"
    (is (= 0.5 (get-in h/tighter-prior-model [:priors :sigma-logMratio :sigma])))
    (is (= 1.0 (get-in h/hmeta-d-group-model [:priors :sigma-logMratio :sigma]))))

  (testing "finite log prior for valid params"
    (let [params {:mu-logMratio 0.0 :sigma-logMratio 0.5 :mu-c2 0.0 :sigma-c2 0.5}]
      (is (Double/isFinite (h/log-prior-group params h/hmeta-d-group-model)))))

  (testing "negative truncated prior returns -Inf"
    (let [params {:mu-logMratio 0.0 :sigma-logMratio -0.1 :mu-c2 0.0 :sigma-c2 0.5}]
      (is (= ##-Inf (h/log-prior-group params h/hmeta-d-group-model)))))

  (testing "tighter prior has lower density off center"
    (let [params {:mu-logMratio 0.0 :sigma-logMratio 0.8 :mu-c2 0.0 :sigma-c2 0.5}
          lp-wide (h/log-prior-group params h/hmeta-d-group-model)
          lp-tight (h/log-prior-group params h/tighter-prior-model)]
      (is (< lp-tight lp-wide))))

  (testing "EDN round trip"
    (let [edn-str (pr-str h/hmeta-d-group-model)
          reloaded (read-string edn-str)]
      (is (= (get-in reloaded [:priors :mu-logMratio :sigma])
             (get-in h/hmeta-d-group-model [:priors :mu-logMratio :sigma])))))

  (testing "fit-group returns configured chain count"
    (let [model (assoc h/hmeta-d-group-model :mcmc {:n-chains 2 :n-samples 5 :n-burnin 2 :step-size 0.05 :seed 11})
          chains (h/fit-group model subject-data)]
      (is (= 2 (count chains)))
      (is (= 5 (count (first chains)))))))
