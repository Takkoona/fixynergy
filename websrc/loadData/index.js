import { useMutantNode, useMutantFreq } from "./useData";
import { parseData } from "./processData";

export function LoadData() {
    const mutantNode = useMutantNode();
    const mutantFreq = useMutantFreq();

    if (mutantFreq && mutantNode) { return parseData(mutantNode, mutantFreq) };
    return;
}
