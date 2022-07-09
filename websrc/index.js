import React from "react";
import { createRoot } from "react-dom/client";
import { LoadData } from "./loadData";
import { MutantMap } from "./mutantMap";
import { DateGraph } from "./dateGraph";

const root = document.getElementById("mutantLandscape");

const landscapeSizeRatio = 0.8;
const dateGraphSizeRatio = 1 - landscapeSizeRatio;

const width = 960;
const height = 600;

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
            ></DateGraph>
            <MutantMap
                landscapeData={landscapeData}
                laneLengths={laneLengths}
                maxRatioSum={maxRatioSum}
                landScapeHeight={height}
                landScapeWidth={width}
            ></MutantMap>
        </svg>
    );
};

createRoot(root).render(<App />);
