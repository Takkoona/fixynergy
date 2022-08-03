import { useState, useEffect } from "react";
import { json, csv } from "d3";
import { LandscapeMap } from "./processData";

const rawDataUrl = "https://gist.githubusercontent.com/Takkoona/854b54ed3148561f95e395350d16ff45/raw/4ad38d75214136e74b4b7bb7f614b42f25a27364";

export function useData() {

    const mutNodeUrl = `${rawDataUrl}/USA_mut_node.json`;
    const mutFreqUrl = `${rawDataUrl}/USA_mut_freq.csv`;

    const [data, setData] = useState(null);

    useEffect(() => {
        Promise.all([
            json(mutNodeUrl),
            csv(mutFreqUrl, d => {
                d["mut_set_id"] = +d["mut_set_id"];
                d["date"] = new Date(d["date"]);
                d["ratio"] = +d["ratio"];
                return d;
            })
        ]).then(([mutantNode, mutantFreq]) => {
            const landscapeMap = new LandscapeMap();
            const [mutDailyFreq, dateRange] = landscapeMap.fromDailyData(mutantNode, mutantFreq);
            setData([landscapeMap, mutDailyFreq, dateRange]);
        })
    }, [mutNodeUrl, mutFreqUrl]);

    return data;
};
