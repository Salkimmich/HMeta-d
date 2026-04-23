(ns hmeta-d.test-runner
  (:gen-class)
  (:import [java.lang System])
  (:require [clojure.test :refer [run-tests]]
            [hmeta-d.sdt-test]
            [hmeta-d.sampler-test]
            [hmeta-d.hierarchical-test]))

(defn -main []
  (let [summary (run-tests 'hmeta-d.sdt-test
                           'hmeta-d.sampler-test
                           'hmeta-d.hierarchical-test)
        failing (+ (:fail summary 0) (:error summary 0))]
    (System/exit (if (pos? failing) 1 0))))
