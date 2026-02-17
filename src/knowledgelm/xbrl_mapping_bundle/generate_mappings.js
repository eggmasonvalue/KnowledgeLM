const fs = require('fs');
const path = require('path');

const XBRL_FILE = path.join(__dirname, 'Ann-xbrl.js');
const FORMAT_FILE = path.join(__dirname, 'Ann-format.js');
const OUTPUT_FILE = path.join(__dirname, 'xbrl_labels.json');

const mappings = {};

function addMapping(key, label) {
    if (!key || !label || typeof key !== 'string' || typeof label !== 'string') return;
    label = label.trim();
    if (label.length === 0) return;

    // Check for collision (same key, DIFFERENT label)
    if (mappings[key] && mappings[key] !== label) {
        // Ignore casing differences or minor whitespace?
        // Let's be strict for now but maybe log it.
        console.warn(`[COLLISION] Key '${key}' has conflicting labels:\n  1. "${mappings[key]}"\n  2. "${label}"\n  Keeping original.`);
        return;
    }

    // 1. Exact match
    mappings[key] = label;

    // 2. Suffix stripping (e.g. key_Rec123 -> key)
    // This is crucial because raw XBRL often uses base keys while JS uses suffixed keys
    if (key.includes('_Rec')) {
        const parts = key.split('_Rec');
        const baseKey = parts[0];
        if (baseKey && baseKey.length > 2) {
            // Check collision for base key too
            if (mappings[baseKey] && mappings[baseKey] !== label) {
                console.warn(`[COLLISION-BASE] Base Key '${baseKey}' (from ${key}) has conflicting labels:\n  1. "${mappings[baseKey]}"\n  2. "${label}"\n  Keeping original.`);
            } else {
                mappings[baseKey] = label;
            }
        }
    }
}

// ---------------------------------------------------------
// 1. Context-Aware Parsing of displayJsonData in Ann-xbrl.js
// ---------------------------------------------------------
console.log(`Processing ${XBRL_FILE}...`);
const xbrlContent = fs.readFileSync(XBRL_FILE, 'utf8');
const lines = xbrlContent.split('\n');

let currentContainer = 'GLOBAL';

for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // A. Detect Container Switch
    const containerMatch = line.match(/if\s*\(\s*containerId\s*===?\s*['"](.*?)['"]/);
    if (containerMatch) {
        currentContainer = containerMatch[1];
    }

    // B. Detect `addRowToTable` (Simple key-value)
    // format: addRowToTable(tableBody, 'Label', newJsonData['Key']);
    const rowMatch = line.match(/addRowToTable\s*\([^,]+,\s*(['"])(.*?)\1\s*,\s*newJsonData\s*\[\s*(['"])(.*?)\3\s*\]/);
    if (rowMatch) {
        addMapping(rowMatch[4], rowMatch[2]);
    }

    // C. Detect `tableColumnData` assignments (Multi-line block)
    if (line.startsWith('tableColumnData = [')) {
        let blockContent = '';
        let j = i + 1;
        while (j < lines.length) {
            const nextLine = lines[j].trim();
            blockContent += nextLine;
            if (nextLine.endsWith('];')) {
                break;
            }
            j++;
        }

        const colRegex = /"name":\s*"([^"]+)",\s*"heading":\s*"([^"]+)"/g;
        let match;
        while ((match = colRegex.exec(blockContent)) !== null) {
            addMapping(match[1], match[2]);
        }
    }

    // D. Detect Hardcoded Arrays (Rec60EventTypeAcquistion)
    // format: singleMappingTableRows = [["Label", key1, key2, key3], ...]
    if (currentContainer === 'Rec60EventTypeAcquistion' && line.startsWith('singleMappingTableRows = [[')) {
        // This is a very specific format for Acquisition keys
        // We extract variable names like _rowData.startYearFirstPrev_Rec60EventTypeAcquistion
        const varRegex = /_rowData\.(\w+)/g;
        // And labels like "1st Previous year turnover"
        // ... but manual extraction is safer here given the complexity
        // Let's use a regex to find ALL _rowData.KEY usage and try to map to nearby strings?
        // Actually, let's just parse the keys from this block
        let match;
        while ((match = varRegex.exec(line)) !== null) {
            const key = match[1];
            // Heuristic: The label is likely close by, but for now capturing the key is enough?
            // No, we need the label.
            // Manual Block for these specific hardcoded keys is cleaner and safer
        }
    }
}

// ---------------------------------------------------------
// 2. Global Variable Parsing (Ann-format.js & Ann-xbrl.js)
// ---------------------------------------------------------
// This fallback is still useful for global mappings like `keyMapping`
function parseGlobalVariables(content) {
    const objArrRegex = /(?:var|const|let|)\s*(\w+)\s*=\s*([\[{][\s\S]*?[\]}]);/g;
    let match;
    while ((match = objArrRegex.exec(content)) !== null) {
        try {
            const valStr = match[2];
            if (valStr.includes('function') || valStr.includes('=>')) continue;
            // specific cleanup for 'keyMapping' and 'selectkeyMapping'
            if (match[1] === 'keyMapping' || match[1] === 'selectkeyMapping' || match[1] === 'xbrlLabels') {
                const data = eval('(' + valStr + ')');
                if (data && typeof data === 'object') {
                    Object.entries(data).forEach(([k, v]) => {
                        if (typeof v === 'string') addMapping(k, v);
                    });
                }
            }
        } catch (e) { }
    }
}
parseGlobalVariables(xbrlContent);
parseGlobalVariables(fs.readFileSync(FORMAT_FILE, 'utf8'));


// ---------------------------------------------------------
// 3. Manual Fallbacks (The "Gap Fillers")
// ---------------------------------------------------------
// Derived from reading the code where addRowToTable is NOT used but keys are present
const manualMappings = {
    // Acquisition (Rec60) - derived from singleMappingTableRows inspection
    "startYearFirstPrev_Rec60EventTypeAcquistion": "1st Previous Year - Start Date",
    "endYearFirstPrev_Rec60EventTypeAcquistion": "1st Previous Year - End Date",
    "turnoverFirstPrev_Rec60EventTypeAcquistion": "1st Previous Year - Turnover",
    "startsecondPrevYear_Rec60EventTypeAcquistion": "2nd Previous Year - Start Date",
    "endsecondPrevYear_Rec60EventTypeAcquistion": "2nd Previous Year - End Date",
    "secondPrevTurnover_Rec60EventTypeAcquistion": "2nd Previous Year - Turnover",
    "startthirdPrevYear_Rec60EventTypeAcquistion": "3rd Previous Year - Start Date",
    "endthirdPrevYear_Rec60EventTypeAcquistion": "3rd Previous Year - End Date",
    "thirdPrevTurnover_Rec60EventTypeAcquistion": "3rd Previous Year - Turnover",
    "countryAcqrdPresence_Rec60EventTypeAcquistion": "Country of Presence",
    "anyOthrBrfSignfInfoAcquston_Rec60EventTypeAcquistion": "Any Other Significant Info"
};

Object.entries(manualMappings).forEach(([k, v]) => addMapping(k, v));

// ---------------------------------------------------------
// 4. Output
// ---------------------------------------------------------
fs.writeFileSync(OUTPUT_FILE, JSON.stringify(mappings, null, 2));
console.log(`Generated ${Object.keys(mappings).length} mappings in ${OUTPUT_FILE}`);
