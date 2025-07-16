// Simple count from the file
import * as XLSX from 'xlsx';

const fileContent = await window.fs.readFile('EUC_ESOL 2.xlsx');
const workbook = XLSX.read(fileContent, { type: 'array' });
const data = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]);

// Just get the basic metrics
const total = data.length;
console.log(`Total devices: ${total}`);

// Sample the data to understand the structure
const sample = data.slice(0, 100);
let urgentCount = 0;
let replaceCount = 0;
let win11Count = 0;

sample.forEach(row => {
  if (row['Action to take'] === 'Urgent Replacement') urgentCount++;
  if (row['Action to take'] === 'Replace by 14/10/2025') replaceCount++;
  if (row['Current OS Build'] && row['Current OS Build'].includes('Win11')) win11Count++;
});

// Extrapolate from sample
const esol2024Est = Math.round((urgentCount / 100) * total);
const esol2025Est = Math.round((replaceCount / 100) * total);
const win11Est = Math.round((win11Count / 100) * total);

console.log(`Estimated ESOL 2024: ${esol2024Est}`);
console.log(`Estimated ESOL 2025: ${esol2025Est}`);
console.log(`Estimated Win11: ${win11Est}`);
console.log(`Total estimate: ${total}`);