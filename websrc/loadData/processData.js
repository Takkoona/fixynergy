import { sum, extent, group, flatGroup } from "d3";
import { mutationName } from "../utils";

const MUT_INFO_LEN = 4;

class LandscapeNode {

    #defaultRatioSum;

    constructor(id, parentLinks, dailyRatio, ratioSum) {
        this.id = id;
        this.dailyRatio = dailyRatio;
        this.parentLinks = parentLinks;
        this.#defaultRatioSum = ratioSum;
    };
    getDefaultRatioSum() { return this.#defaultRatioSum; };
    setCoord(x, y) {
        this.x = x;
        this.y = y;
        return this;
    };
    getCoord() { return [this.x, this.y]; };
    resetDateRange() {
        this.ratioSum = this.#defaultRatioSum;
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
    setMutSelection(startingMuts, selectedMuts) {
        let mutantNames = [];
        for (let i = 0; i < this.parentLinks.length; i++) {
            const [, [p, n, s]] = this.parentLinks[i];
            const mutName = mutationName(p, n, s);
            if (!selectedMuts.includes(mutName)) {
                return false;
            };
            mutantNames.push(mutName);
        };
        return startingMuts.every(mut => mutantNames.includes(mut));
    };
    getMutName() {
        return this.parentLinks.map(([, [p, n, s]]) => {
            return mutationName(p, n, s);
        }).join(", ");
    };
};

class LandscapeMap {

    #defaultData;
    #defaultStartIndex;
    #defaultEndIndex;

    constructor(data, startIndex, endIndex, maxRatioSum) {
        this.#defaultData = data;
        this.#defaultStartIndex = startIndex;
        this.#defaultEndIndex = endIndex
        this.maxRatioSum = maxRatioSum;
        this.resetMutSelection();
    };
    getStartEndIndex() { return [this.startIndex, this.endIndex]; };
    resetDateRange() {
        this.data.forEach(laneData => {
            laneData.forEach(mutSetNode => {
                mutSetNode.resetDateRange();
            });
        });
        return this;
    };
    setDateRange(dateRange) {
        this.data.forEach(laneData => {
            laneData.forEach(mutSetNode => {
                mutSetNode.setDateRange(...dateRange);
            });
        });
        return this;
    };
    resetMutSelection() {
        this.startIndex = this.#defaultStartIndex;
        this.endIndex = this.#defaultEndIndex;
        this.data = this.#defaultData;
        return this;
    };
    setMutSelection(startingMuts, selectedMuts) {
        const laneTracker = new LaneInfoTracker();
        this.data = this.#defaultData.map((laneData, laneIndex) => {
            const nodesToKeep = [];
            let laneRatioSum = 0;
            laneData.forEach(mutSetNode => {
                if (mutSetNode.setMutSelection(
                    startingMuts,
                    selectedMuts
                )) {
                    nodesToKeep.push(mutSetNode);
                    laneRatioSum += mutSetNode.getDefaultRatioSum();
                };
            });
            laneTracker.findStartEndIndex(laneIndex, laneRatioSum);
            return nodesToKeep;
        });
        this.startIndex = laneTracker.startIndex;
        this.endIndex = laneTracker.endIndex;
        return this;
    };
    #setStartEndIndex(laneIndex, laneRatioSum) {
        if (laneRatioSum && this.startIndex === null) {
            this.startIndex = laneIndex;
        };
        if (!laneRatioSum && this.startIndex !== null && this.endIndex === null) {
            this.endIndex = laneIndex;
        };
    };
};

class LaneInfoTracker {
    // This can be integrated into class LandscapeMap
    constructor() {
        this.startIndex = null;
        this.endIndex = null;
    };
    findStartEndIndex(laneIndex, laneRatioSum) {
        if (laneRatioSum && this.startIndex === null) {
            this.startIndex = laneIndex;
        };
        if (!laneRatioSum && this.startIndex !== null && this.endIndex === null) {
            this.endIndex = laneIndex;
        };
    };
}

export function parseData(mutantNode, mutantFreq) {
    const groupedMutFreq = group(mutantFreq, d => d["mut_set_id"]);
    const mutFreq = [];
    const landscapeData = [];
    let laneData = [];
    const prevLaneData = new Map();
    let laneRatioSum = 0, laneIndex = -1;
    const laneTracker = new LaneInfoTracker();
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
            laneTracker.findStartEndIndex(laneIndex, laneRatioSum);
            laneIndex++;
            laneRatioSum = 0;
        };
        const ratioSum = sum(dailyRatio, d => d["ratio"]);
        laneRatioSum += ratioSum;
        if (ratioSum > maxRatioSum) { maxRatioSum = ratioSum; };
        const mutSetNode = new LandscapeNode(
            mutSetId,
            parentLinks,
            dailyRatio,
            ratioSum
        );
        prevLaneData.set(mutSetId, mutSetNode);
        laneData.push(mutSetNode);
        prevMutLinkLength = mutLink.length;
    });
    landscapeData.push(laneData);
    landscapeData.shift();
    // Decide start and end index based on laneRatioSum of each lane
    laneTracker.findStartEndIndex(laneIndex, laneRatioSum);
    const landscapeMap = new LandscapeMap(
        landscapeData,
        laneTracker.startIndex,
        laneTracker.endIndex,
        maxRatioSum
    );
    const dailyMutFreq = flatGroup(
        mutFreq,
        d => d["mut"],
        d => d["date"]
    ).map(([n, d, ratio]) => {
        return {
            "mut": n,
            "date": d,
            "ratio": sum(ratio, r => r["ratio"])
        };
    });
    const dateRange = extent(dailyMutFreq, d => d["date"]);
    const mutDailyFreq = group(dailyMutFreq, d => d["mut"]);
    return [landscapeMap, mutDailyFreq, dateRange];
};
