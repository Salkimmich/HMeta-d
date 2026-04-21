(ns hmeta-d.test-runner
  (:require [clojure.test :refer [run-tests]]
            [hmeta-d.sdt-test]
            [hmeta-d.sampler-test]
            [hmeta-d.hierarchical-test]))

(defn -main []
  (run-tests 'hmeta-d.sdt-test
             'hmeta-d.sampler-test
             'hmeta-d.hierarchical-test))
