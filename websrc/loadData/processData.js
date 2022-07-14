import { sum, extent, group, flatGroup } from "d3";
import { mutationName } from "../utils";

const MUT_INFO_LEN = 4;

class LandscapeNode {
    constructor(id, parentLinks, dailyRatio, ratioSum, laneIndex) {
        this.id = id;
        this.parentLinks = parentLinks;
        this.dailyRatio = dailyRatio;
        this.ratioSum = ratioSum;
        this.laneIndex = laneIndex;
    }
    setCoord(xScale, yScales) {
        this.x = xScale(this.parentLinks.length);
        this.y = yScales.at(this.parentLinks.length)(this.laneIndex + 1);
        return this;
    }
    getCoord() { return [this.x, this.y]; }
    setDateRange(startDate, endDate) {
        this.ratioSum = 0;
        for (let i = 0; i < this.dailyRatio.length; i++) {
            const currDate = this.dailyRatio[i]["date"];
            if (currDate >= startDate && currDate <= endDate) {
                this.ratioSum += this.dailyRatio[i]["ratio"];
            }
        }
        return this;
    }
    getMutName() {
        return this.parentLinks.map(([, [p, n, s]]) => mutationName(p, n, s)).join(", ");
    }
}

export function parseData(mutantNode, mutantFreq) {
    const groupedMutFreq = group(mutantFreq, d => d["mut_set_id"]);
    const mutFreq = [];
    // TODO: use Map for parent retrieve and return a nested array
    // "laneLengths" and "laneExist" won't be needed this way
    const landscapeData = new Map();
    const laneLengths = [];
    const laneExist = [];
    let laneRatioSum = 0;
    let laneIndex = 0;
    let prevMutLinkLength = -1;
    let maxRatioSum = -1;
    mutantNode.forEach(([mutSetId, ...mutLink]) => {

        const dailyRatio = groupedMutFreq.get(mutSetId) || [];
        const ratioSum = sum(dailyRatio, d => d["ratio"]);
        if (ratioSum > maxRatioSum) { maxRatioSum = ratioSum; };
        laneRatioSum += ratioSum;

        const parentLinks = [];
        for (let i = 0; i < mutLink.length; i += MUT_INFO_LEN) {
            const [parentId, ...mut] = mutLink.slice(i, i + MUT_INFO_LEN);
            parentLinks.push([landscapeData.get(parentId), mut]);
            for (let j = 0; j < dailyRatio.length; j++) {
                mutFreq.push({
                    "mut": mutationName(...mut),
                    "date": dailyRatio[j]["date"],
                    "ratio": dailyRatio[j]["ratio"]
                });
            };
        };
        if (mutLink.length > prevMutLinkLength) {
            laneLengths.push(laneIndex); // incremented in the last loop, should be length now
            laneIndex = 0;
            laneExist.push(Boolean(laneRatioSum)); // Total ratioSum of the last lane
            laneRatioSum = 0;
        };
        const mutSetNode = new LandscapeNode(
            mutSetId,
            parentLinks,
            dailyRatio,
            ratioSum,
            laneIndex++
        );
        landscapeData.set(mutSetId, mutSetNode);
        prevMutLinkLength = mutLink.length;
    });
    laneLengths.push(laneIndex);
    laneLengths.shift(); // Remove the first
    laneExist.push(Boolean(laneRatioSum));
    laneExist.shift(); // Remove the first
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
        laneLengths,
        laneExist,
        dailyMutFreq,
        maxRatioSum,
        dateRange
    ];
}
