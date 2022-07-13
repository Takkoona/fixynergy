import { useMutantNode, useMutantFreq } from "./useData";
import { parseData } from "./processData";

const rawDataUrl = "https://gist.githubusercontent.com/Takkoona/854b54ed3148561f95e395350d16ff45/raw/4ad38d75214136e74b4b7bb7f614b42f25a27364";

export function LoadData() {

    const mutNodeUrl = `${rawDataUrl}/USA_mut_node.json`;
    const mutFreqUrl = `${rawDataUrl}/USA_mut_freq.csv`;

    const mutantNode = useMutantNode(mutNodeUrl);
    const mutantFreq = useMutantFreq(mutFreqUrl);

    if (mutantFreq && mutantNode) { return parseData(mutantNode, mutantFreq) };
    return;
}
