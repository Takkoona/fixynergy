import { useState, useEffect } from 'react';
import { csv, json } from 'd3';

const mutNodeUrl = "https://gist.githubusercontent.com/Takkoona/854b54ed3148561f95e395350d16ff45/raw/4ad38d75214136e74b4b7bb7f614b42f25a27364/USA_mut_node.json";
const mutFreqUrl = "https://gist.githubusercontent.com/Takkoona/854b54ed3148561f95e395350d16ff45/raw/4ad38d75214136e74b4b7bb7f614b42f25a27364/USA_mut_freq.csv";

export function useMutantNode() {
    const [data, setData] = useState(null);
    useEffect(() => { json(mutNodeUrl).then(setData); }, []);
    return data;
};

export function useMutantFreq() {
    const [data, setData] = useState(null);
    useEffect(() => {
        csv(mutFreqUrl, d => {
            d["mut_set_id"] = +d["mut_set_id"];
            d["date"] = new Date(d["date"]);
            d["ratio"] = +d["ratio"];
            return d;
        }).then(setData);
    }, []);
    return data;
};
