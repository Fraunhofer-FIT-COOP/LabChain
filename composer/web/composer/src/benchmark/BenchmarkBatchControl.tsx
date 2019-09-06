import React from "react";
import ApplyBenchmarkControl from "../ApplyBenchmarkControl";

export default function BenchmarkControl(props: any) {
    let sendBenchmark = function(benchmarkType: string) {};
    return <ApplyBenchmarkControl clicked={sendBenchmark}></ApplyBenchmarkControl>;
}
