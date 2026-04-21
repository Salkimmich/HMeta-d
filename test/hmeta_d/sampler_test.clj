(ns hmeta-d.sampler-test
  (:require [clojure.test :refer [deftest testing is]]
            [hmeta-d.sampler :as sampler]
            [hmeta-d.sdt :as sdt]))

(def reference-data
  (sdt/prepare-sdt-data
   [36 24 17 20 10 12 34 22]
   [21 19 23 28 33 28 20 19]))

(deftest type2-rate-estimation-tests
  (testing "estimated rates have expected length and range"
    (let [rates (sampler/estimate-type2-rates 0.9 (:c1 reference-data) [0.3 0.6 0.9] (:nratings reference-data))]
      (is (= (dec (:nratings reference-data)) (count (:far-s1 rates))))
      (is (= (dec (:nratings reference-data)) (count (:hr-s2 rates))))
      (is (every? #(and (>= % 0.0) (<= % 1.0)) (:far-s1 rates)))
      (is (every? #(and (>= % 0.0) (<= % 1.0)) (:hr-s2 rates))))))

(deftest log-likelihood-tests
  (testing "valid params return finite log-likelihood"
    (let [ll (sampler/log-likelihood {:meta-d 1.0 :c2 [0.25 0.55 0.8]} reference-data)]
      (is (Double/isFinite ll))))
  (testing "non-positive criteria are rejected"
    (is (= ##-Inf
           (sampler/log-likelihood {:meta-d 1.0 :c2 [0.25 -0.1 0.8]} reference-data)))))

(deftest mh-chain-tests
  (testing "mh-chain returns configured number of samples"
    (let [init {:meta-d 0.8 :c2 [0.4 0.6 0.8]}
          chain (sampler/mh-chain init (assoc reference-data :mcmc {:n-samples 20 :n-burnin 10}) 0.05)]
      (is (= 20 (count chain)))
      (is (map? (last chain)))
      (is (contains? (last chain) :meta-d)))))
