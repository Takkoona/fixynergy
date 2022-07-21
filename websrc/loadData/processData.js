import { sum, extent, group, flatGroup } from "d3";
import { mutationName } from "../utils";

const MUT_INFO_LEN = 4;

class LandscapeNode {

    #defaultRatioSum;

    constructor(id, parentLinks, dailyRatio, ratioSum) {
        this.id = id;
        this.parentLinks = parentLinks;
        this.dailyRatio = dailyRatio;
        this.#defaultRatioSum = ratioSum;
    };
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
    getMutName() {
        return this.parentLinks.map(([, [p, n, s]]) => mutationName(p, n, s)).join(", ");
    };
};

class LandscapeMap {

    #defaultStartIndex;
    #defaultEndIndex;
    #defaultMaxRatioSum;

    constructor(data, startIndex, endIndex, maxRatioSum) {
        this.data = data;
        this.#defaultStartIndex = startIndex;
        this.#defaultEndIndex = endIndex
        this.#defaultMaxRatioSum = maxRatioSum;
        this.resetRenderPrep();
    };
    getStartEndIndex() { return [this.startIndex, this.endIndex]; };
    resetRenderPrep() {
        this.startIndex = this.#defaultStartIndex;
        this.endIndex = this.#defaultEndIndex;
        this.maxRatioSum = this.#defaultMaxRatioSum;
        this.data.map(laneData => {
            laneData.forEach(mutSetNode => {
                mutSetNode.resetDateRange();
            });
        });
        return this;
    };
    setDateRange(dateRange) {
        this.data.map(laneData => {
            let laneRatioSum = 0;
            laneData.forEach(mutSetNode => {
                mutSetNode.setDateRange(...dateRange);
                laneRatioSum += mutSetNode.ratioSum;
            });
        });
        return this;
    };
    setMutationsAndDateRange(mutations, dateRange) {
        this.startIndex = null;
        this.endIndex = null;
        this.data.map((laneData, index) => {
            let laneRatioSum = 0;
            laneData.forEach(mutSetNode => {
                mutSetNode.setDateRange(...dateRange);
                laneRatioSum += mutSetNode.ratioSum;
            });
            this.#findStartEndIndex(laneRatioSum, index);
        });
        return this;
    };
    #findStartEndIndex(laneRatioSum, index) {
        if (laneRatioSum && this.startIndex === null) {
            this.startIndex = index;
        };
        if (!laneRatioSum && this.startIndex !== null && this.endIndex === null) {
            this.endIndex = index;
        };
    };
};

export function parseData(mutantNode, mutantFreq) {
    const groupedMutFreq = group(mutantFreq, d => d["mut_set_id"]);
    const mutFreq = [];
    const landscapeData = [];
    let laneData = [];
    const prevLaneData = new Map();
    let laneRatioSum = 0, laneIndex = -1, startIndex = null, endIndex = null;
    let prevMutLinkLength = -1;
    let maxRatioSum = -1;

    function findStartEndIndex() {
        if (laneRatioSum && startIndex === null) {
            startIndex = laneIndex;
        };
        if (!laneRatioSum && startIndex !== null && endIndex === null) {
            endIndex = laneIndex;
        };
        return [++laneIndex, startIndex, endIndex, 0];
    }

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
            // Decide start and end index based on laneRatioSum of each lane
            [laneIndex, startIndex, endIndex, laneRatioSum] = findStartEndIndex();
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
    [laneIndex, startIndex, endIndex, laneRatioSum] = findStartEndIndex();
    const landscapeMap = new LandscapeMap(
        landscapeData,
        startIndex,
        endIndex,
        maxRatioSum
    );
    const dailyMutFreq = flatGroup(
        mutFreq,
        d => d["mut"],
        d => d["date"]
    ).map(([n, d, ratio]) => {
        return { "mut": n, "date": d, "ratio": sum(ratio, r => r["ratio"]) };
    });
    const dateRange = extent(dailyMutFreq, d => d["date"]);
    const mutDailyFreq = group(dailyMutFreq, d => d["mut"]);
    return [landscapeMap, mutDailyFreq, dateRange];
};
