import React from "react";
import { scaleLinear, scaleSqrt } from "d3";
import { MutantNode } from "./MutantNode";

const margin = { top: 40, right: 50, bottom: 40, left: 50 }

export function MutantMap({
    landscapeData,
    laneLengths,
    maxRatioSum,
    width,
    height
}) {

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = scaleLinear()
        .domain([0, laneLengths.length])
        .range([margin.right, innerWidth]);
    const yScales = laneLengths.map(l => {
        return scaleLinear()
            .domain([0, l + 1])
            .range([innerHeight, margin.bottom])
    });

    const lineScale = scaleLinear().domain([0, maxRatioSum]).range([0, 30]);
    const nodeSizeScale = scaleSqrt().domain([0, maxRatioSum]).range([0, 100]);

    return <MutantNode
        landscapeData={landscapeData}
        xScale={xScale}
        yScales={yScales}
        lineScale={lineScale}
        nodeSizeScale={nodeSizeScale}
    ></MutantNode>;
};
