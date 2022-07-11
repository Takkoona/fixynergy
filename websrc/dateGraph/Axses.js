import React from "react";

export function AxisBottom({ xScale, innerHeight, xAxisTickFormat, tickOffset }) {
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
                y={innerHeight + tickOffset}
            >{xAxisTickFormat(tickValue)}</text>
        </g>
    ));
}

export function AxisLeft({ yScale, innerWidth, tickOffset }) {
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
                x={-tickOffset}
            >{tickValue}</text>
        </g>
    ));
}
