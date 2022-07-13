import { useState, useEffect } from 'react';
import { csv, json } from 'd3';

export function useMutantNode(mutNodeUrl) {
    const [data, setData] = useState(null);
    useEffect(() => { json(mutNodeUrl).then(setData); }, [mutNodeUrl]);
    return data;
};

export function useMutantFreq(mutFreqUrl) {
    const [data, setData] = useState(null);
    useEffect(() => {
        csv(mutFreqUrl, d => {
            d["mut_set_id"] = +d["mut_set_id"];
            d["date"] = new Date(d["date"]);
            d["ratio"] = +d["ratio"];
            return d;
        }).then(setData);
    }, [mutFreqUrl]);
    return data;
};
