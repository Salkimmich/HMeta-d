(ns hmeta-d.test-runner
  (:require [clojure.test :refer [run-tests]]
            [hmeta-d.sdt-test]
            [hmeta-d.sampler-test]))

(defn -main []
  (run-tests 'hmeta-d.sdt-test
             'hmeta-d.sampler-test))
