import React, { useEffect, useRef } from "react";
import { timeFormat, scaleTime, scaleLinear, line, brushX, select } from "d3";
import { setMutOpacity } from "../utils";

const margin = { top: 10, right: 200, bottom: 20, left: 30 };

const xValue = d => d["date"];
const xAxisTickFormat = timeFormat('%m/%d/%Y');
const xTickOffset = 10;

const yValue = d => d["ratio"];
const yTickOffset = 10;

export function DateGraph({
    mutDailyFreq,
    mutColorScale,
    dateRange,
    width,
    height,
    hoveredMut,
    setBrushExtent
}) {

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    const brushRef = useRef();
    
    const xScale = scaleTime().domain(dateRange).range([0, innerWidth]);
    const yScale = scaleLinear().domain([0, 1]).range([innerHeight, 0]);

    useEffect(() => {
        const brush = brushX().extent([[0, 0], [innerWidth, innerHeight]]);
        brush(select(brushRef.current));
        brush.on("brush end", (event) => {
            setBrushExtent(event.selection && event.selection.map(xScale.invert));
        });
    }, [innerWidth, innerHeight]);

    return (
        <g transform={`translate(${margin.left}, ${margin.top})`}>
            <DotMarks
                groupedData={mutDailyFreq}
                xScale={xScale}
                yScale={yScale}
                colorScale={mutColorScale}
                hoveredMut={hoveredMut}
            ></DotMarks>
            <AxisBottom
                xScale={xScale}
                innerHeight={innerHeight}
            ></AxisBottom>
            <AxisLeft
                yScale={yScale}
                innerWidth={innerWidth}
            ></AxisLeft>
            <g ref={brushRef}></g>
        </g>
    );
};

function AxisBottom({ xScale, innerHeight }) {
    return xScale.ticks().map(tickValue => (
        <g key={tickValue} transform={`translate(${xScale(tickValue)}, 0)`}>
            <line
                strokeWidth="1"
                stroke="black"
                opacity="0.1"
                y2={innerHeight}
            ></line>
            <text
                style={{ textAnchor: 'middle' }}
                y={innerHeight + xTickOffset}
                dy=".71em"
                fontSize="10"
            >{xAxisTickFormat(tickValue)}</text>
        </g>
    ));
}

function AxisLeft({ yScale, innerWidth }) {
    return yScale.ticks().map(tickValue => (
        <g key={tickValue} transform={`translate(0,${yScale(tickValue)})`}>
            <line
                strokeWidth="1"
                stroke="black"
                opacity="0.1"
                x2={innerWidth}
            ></line>
            <text
                style={{ textAnchor: 'end' }}
                x={-yTickOffset}
                dy=".32em"
                fontSize="10"
            >{tickValue}</text>
        </g>
    ));
}

function DotMarks({
    groupedData,
    xScale,
    yScale,
    colorScale,
    hoveredMut
}) {
    return Array.from(groupedData).map(([mut, data]) => {
        const linePath = line().x(d => xScale(xValue(d))).y(d => yScale(yValue(d)));
        data = data.sort((a, b) => xValue(a) - xValue(b));
        return (
            <g key={mut} opacity={setMutOpacity(hoveredMut, mut)}>
                <path
                    key={`${mut}line`}
                    fill="none"
                    stroke={colorScale(mut)}
                    d={linePath(data)}
                ></path>
                {data.map(d => (
                    <circle
                        key={`${d["mut"]}${xAxisTickFormat(xValue(d))}`}
                        cx={xScale(xValue(d))}
                        cy={yScale(yValue(d))}
                        r="2"
                        fill={colorScale(mut)}
                        opacity={setMutOpacity(hoveredMut, mut)}
                    ></circle>
                ))}
            </g>
        )
    });
}
