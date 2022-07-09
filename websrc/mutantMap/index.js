import React from "react";
import { scaleLinear, scaleSqrt } from "d3";
import { MutantNode } from "./MutantNode";

const margin = { top: 20, right: 30, bottom: 20, left: 30 }

export function MutantMap({
    landscapeData,
    laneLengths,
    maxRatioSum,
    landScapeHeight,
    landScapeWidth
}) {

    const innerHeight = landScapeHeight - margin.top - margin.bottom;
    const innerWidth = landScapeWidth - margin.left - margin.right;

    const xScale = scaleLinear()
        .domain([0, laneLengths.length])
        .range([margin.right, innerWidth]);
    const yScales = laneLengths.map(l => {
        return scaleLinear()
            .domain([0, l + 1])
            .range([innerHeight, margin.bottom])
    });

    const lineScale = scaleLinear().domain([0, maxRatioSum]).range([0, 30]);
    const nodeSizeScale = scaleSqrt().domain([0, maxRatioSum]).range([0, 30]);

    return <MutantNode
        landscapeData={landscapeData}
        xScale={xScale}
        yScales={yScales}
        lineScale={lineScale}
        nodeSizeScale={nodeSizeScale}
    ></MutantNode>;
};
