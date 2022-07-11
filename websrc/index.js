import React from "react";
import { createRoot } from "react-dom/client";
import { LoadData } from "./loadData";
import { MutantMap } from "./mutantMap";
import { DateGraph } from "./dateGraph";

const root = document.getElementById("mutantLandscape");

const width = 1200;
const height = 600;

const landscapeSpecs = { h: 0.7, w: 1 };
const dateGraphSpecs = { h: 1 - landscapeSpecs.h, w: 1 };

const App = () => {

    const data = LoadData();
    if (!data) return <pre>Loading...</pre>
    const [
        landscapeData,
        laneLengths,
        dailyMutFreq,
        maxRatioSum
    ] = data;

    return (
        <svg width={width} height={height}>
            <DateGraph
                dailyMutFreq={dailyMutFreq}
                width={width * dateGraphSpecs.w}
                height={height * dateGraphSpecs.h}
            ></DateGraph>
            <g transform={`translate(0, ${height * dateGraphSpecs.h})`}>
            <MutantMap
                landscapeData={landscapeData}
                laneLengths={laneLengths}
                maxRatioSum={maxRatioSum}
                width={width * landscapeSpecs.w}
                height={height * landscapeSpecs.h}
            ></MutantMap>
            </g>
        </svg>
    );
};

createRoot(root).render(<App />);
