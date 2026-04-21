(ns hmeta-d.sdt-test
  (:require [clojure.test :refer [deftest is testing run-tests]]
            [hmeta-d.sdt :as sdt]))

(def reference-nR-S1 [36 24 17 20 10 12 34 22])
(def reference-nR-S2 [21 19 23 28 33 28 20 19])

(deftest phase1-reference-inputs
  (testing "Clojure SDT core matches MATLAB-equivalent Python reference values"
    (let [{:keys [d1 c1 nratings nTot counts]}
          (sdt/prepare-sdt-data reference-nR-S1 reference-nR-S2)]
      (is (= 4 nratings))
      (is (= (+ (reduce + reference-nR-S1)
                (reduce + reference-nR-S2))
             nTot))
      (is (= 16 (count counts)))
      (is (< (Math/abs (- d1 0.1945)) 0.001))
      (is (< (Math/abs (- c1 0.0385)) 0.001)))))

(defn -main []
  (run-tests 'hmeta-d.sdt-test))
