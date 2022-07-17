import { sum, extent, group, flatGroup } from "d3";
import { mutationName } from "../utils";

const MUT_INFO_LEN = 4;

class LandscapeNode {
    constructor(id, parentLinks, dailyRatio) {
        this.id = id;
        this.parentLinks = parentLinks;
        this.dailyRatio = dailyRatio;
        this.resetDateRange();
    };
    setCoord(x, y) {
        this.x = x;
        this.y = y;
        return this;
    };
    getCoord() { return [this.x, this.y]; };
    resetDateRange() {
        this.ratioSum = 0;
        for (let i = 0; i < this.dailyRatio.length; i++) {
            this.ratioSum += this.dailyRatio[i]["ratio"];
        };
        return this;
    };
    setDateRange(startDate, endDate) {
        this.ratioSum = 0;
        for (let i = 0; i < this.dailyRatio.length; i++) {
            const currDate = this.dailyRatio[i]["date"];
            if (currDate >= startDate && currDate <= endDate) {
                this.ratioSum += this.dailyRatio[i]["ratio"];
            };
        };
        return this;
    };
    getMutName() {
        return this.parentLinks.map(([, [p, n, s]]) => mutationName(p, n, s)).join(", ");
    };
};

export function parseData(mutantNode, mutantFreq) {
    const groupedMutFreq = group(mutantFreq, d => d["mut_set_id"]);
    const mutFreq = [];
    // TODO: use Map for parent retrieve and return a nested array
    // "laneLengths" and "laneExist" won't be needed this way
    const landscapeData = [];
    let laneData = [];
    const prevLaneData = new Map();
    let prevMutLinkLength = -1;
    let maxRatioSum = -1;
    mutantNode.forEach(([mutSetId, ...mutLink]) => {
        const dailyRatio = groupedMutFreq.get(mutSetId) || [];
        const parentLinks = [];
        for (let i = 0; i < mutLink.length; i += MUT_INFO_LEN) {
            const [parentId, ...mut] = mutLink.slice(i, i + MUT_INFO_LEN);
            parentLinks.push([prevLaneData.get(parentId), mut]);
            for (let j = 0; j < dailyRatio.length; j++) {
                mutFreq.push({
                    "mut": mutationName(...mut),
                    "date": dailyRatio[j]["date"],
                    "ratio": dailyRatio[j]["ratio"]
                });
            };
        };
        if (mutLink.length > prevMutLinkLength) {
            landscapeData.push(laneData);
            laneData = [];
        };
        const mutSetNode = new LandscapeNode(
            mutSetId,
            parentLinks,
            dailyRatio,
        );
        prevLaneData.set(mutSetId, mutSetNode);
        laneData.push(mutSetNode);
        const ratioSum = mutSetNode.ratioSum;
        if (ratioSum > maxRatioSum) { maxRatioSum = ratioSum; };
        prevMutLinkLength = mutLink.length;
    });
    landscapeData.push(laneData);
    landscapeData.shift();
    const dailyMutFreq = flatGroup(
        mutFreq,
        d => d["mut"],
        d => d["date"]
    ).map(([n, d, ratio]) => {
        return { "mut": n, "date": d, "ratio": sum(ratio, r => r["ratio"]) };
    });
    const dateRange = extent(dailyMutFreq, d => d["date"]);
    return [
        landscapeData,
        dailyMutFreq,
        maxRatioSum,
        dateRange
    ];
}
