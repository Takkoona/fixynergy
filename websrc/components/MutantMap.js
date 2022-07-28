import React, { useState, useEffect, useRef } from "react";
import { scaleLinear, scaleSqrt, max, pie, arc } from "d3";
import { mutationName, setMutOpacity } from "../utils";

const margin = { top: 40, right: 200, bottom: 40, left: 40 }
const defaultMaxNodeSize = 100;
const nodeChangeSize = 20;

export function MutantMap({
    landscapeMap,
    mutColorScale,
    width,
    height,
    hoveredMut,
    brushExtent,
    selectedMuts
}) {

    const [maxNodeSize, setMaxNodeSize] = useState(defaultMaxNodeSize);
    const mutatnMapRef = useRef(null);

    useEffect(() => {
        const handler = event => {
            // event.preventDefault();
            if (event.deltaY < 0) {
                setMaxNodeSize(prevMaxNodeSize => prevMaxNodeSize + nodeChangeSize);
            }
            if (event.deltaY > 0) {
                setMaxNodeSize(prevMaxNodeSize => prevMaxNodeSize - nodeChangeSize);
            };
            if (event.ctrlKey) {
                if (event.key === "0") {
                    setMaxNodeSize(defaultMaxNodeSize);
                }
            }
        };
        const element = mutatnMapRef.current;
        element.addEventListener("wheel", handler);
        document.addEventListener('keydown', handler);
        return () => {
            element.removeEventListener("wheel", handler);
            document.removeEventListener('keydown', handler);
        }
    }, []);
    // console.log(maxNodeSize);
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    if (brushExtent) {
        landscapeMap.setDateRange(brushExtent);
    } else {
        landscapeMap.resetDateRange();
    };
    if (selectedMuts.length) {
        landscapeMap.setMutSelection([], selectedMuts);
    } else {
        landscapeMap.resetMutSelection();
    };

    const [startIndex, endIndex] = landscapeMap.getStartEndIndex();
    const xScale = scaleLinear().domain([startIndex, endIndex - 1]).range([0, innerWidth]);
    const nodeSizeScale = scaleSqrt().domain([0, landscapeMap.maxRatioSum]).range([0, maxNodeSize]);

    return (
        <g transform={`translate(${margin.left}, ${margin.top})`} ref={mutatnMapRef}>
            <rect width={innerWidth} height={innerHeight} fill="white"></rect>
            {landscapeMap.data.map((laneData, laneIndex) => {
                const yScale = scaleLinear().domain([0, laneData.length + 1]).range([innerHeight, 0]);
                return (
                    <MutantLane
                        key={`lane_${laneIndex}`}
                        laneData={laneData}
                        mutColorScale={mutColorScale}
                        xScale={xScale}
                        yScale={yScale}
                        nodeSizeScale={nodeSizeScale}
                        hoveredMut={hoveredMut}
                        selectedMuts={selectedMuts}
                    ></MutantLane>
                )
            })}
        </g>
    );
};

function MutantLane({
    laneData,
    mutColorScale,
    xScale,
    yScale,
    nodeSizeScale,
    hoveredMut,
    selectedMuts
}) {
    return laneData.map((mutSetNode, nodeIndex) => {
        const x = xScale(mutSetNode.parentLinks.length);
        const y = yScale(nodeIndex + 1);
        mutSetNode.setCoord(x, y);
        if (mutSetNode.ratioSum === 0) { return undefined; };
        const mutSetId = mutSetNode.id;
        const mutIncreValues = [];
        const pieRadius = nodeSizeScale(mutSetNode.ratioSum);
        const arcScale = arc().innerRadius(0).outerRadius(pieRadius);
        const pieScale = pie().value(d => d["ratioDiff"]);
        return (
            <g key={mutSetId}>
                {mutSetNode.parentLinks.map(([parent, mut]) => {
                    const mutName = mutationName(...mut);
                    const ratioDiff = mutSetNode.ratioSum - parent.ratioSum;
                    mutIncreValues.push({ mutName, ratioDiff });
                    return (
                        <line
                            key={[mutSetId, parent.id].join(",")}
                            x1={parent.x}
                            y1={parent.y}
                            x2={x}
                            y2={y}
                            strokeWidth="1"
                            opacity={setMutOpacity(
                                hoveredMut,
                                mutName,
                                selectedMuts,
                                0,
                                max([ratioDiff, 0])
                            )}
                            stroke={mutColorScale(mutName)}
                        >
                            <title>{`Mutation: ${mutName}`}</title>
                        </line>
                    );
                })}
                <g transform={`translate(${x}, ${y})`}>
                    {pieScale(mutIncreValues).map(({
                        data,
                        startAngle,
                        endAngle
                    }) => {
                        const mutName = data["mutName"];
                        const pieArcColor = mutColorScale(mutName);
                        const arcPathGen = arcScale.startAngle(startAngle).endAngle(endAngle);
                        return (
                            <path
                                key={`${mutSetId}${mutName}_pie`}
                                d={arcPathGen()}
                                fill={pieArcColor}
                                fillOpacity={setMutOpacity(
                                    hoveredMut,
                                    mutName,
                                    selectedMuts,
                                    0.05,
                                    0.5
                                )}
                                stroke={pieArcColor}
                                strokeOpacity={setMutOpacity(
                                    hoveredMut,
                                    mutName,
                                    selectedMuts
                                )}
                            >
                                <title>{`${data["mutName"]} (${mutSetNode.getMutName()})`}</title>
                            </path>
                        )
                    })}
                </g>
                <circle
                    key={mutSetId.toString() + "node"}
                    cx={x}
                    cy={y}
                    r={pieRadius}
                    fill="none"
                    stroke="#d3d3d3"
                    strokeWidth="1"
                >
                    <title>{mutSetNode.getMutName()}</title>
                </circle>
            </g>
        );
    });
};
