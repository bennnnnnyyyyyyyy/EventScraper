/**
 * BD26-EVENT — Apps Script Backend for Prospect Scraping
 * Connected Sheet: https://docs.google.com/spreadsheets/d/1LNG9nhDE62LKBya4pD9NsUagJwcmK0_sxspS4LsY5iE/edit
 */

const SPREADSHEET_ID = "1LNG9nhDE62LKBya4pD9NsUagJwcmK0_sxspS4LsY5iE";
const SHEET_NAME = "Prospects";

const HEADER = [
  "Company",
  "Domain",
  "Source",
  "Name",
  "Title",
  "Email",
  "LinkedIn URL",
  "Contact ID",
  "Date Added"
];

function getOrCreateSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.getSheets()[0];
    sheet.setName(SHEET_NAME);
  }

  // Ensure header row exists
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADER);
    sheet.getRange(1, 1, 1, HEADER.length).setFontWeight("bold").setBackground("#f3f3f3");
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getExistingKeys(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return {};

  // Read columns: Email (col 6), LinkedIn (col 7), ID (col 8)
  const data = sheet.getRange(2, 1, lastRow - 1, 9).getValues();
  const keys = {};

  for (let i = 0; i < data.length; i++) {
    const row = data[i];
    const email = String(row[5] || "").trim().toLowerCase();
    const linkedin = String(row[6] || "").trim().toLowerCase();
    const contactId = String(row[7] || "").trim().toLowerCase();

    if (linkedin) keys[linkedin] = true;
    if (email) keys[email] = true;
    if (contactId) keys[contactId] = true;
  }
  return keys;
}

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action) || "status";
  const sheet = getOrCreateSheet();

  if (action === "get_keys") {
    const keys = getExistingKeys(sheet);
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      count: Object.keys(keys).length,
      keys: Object.keys(keys)
    })).setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    project: "BD26-EVENT",
    spreadsheetId: SPREADSHEET_ID,
    totalRows: Math.max(0, sheet.getLastRow() - 1)
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const contents = e.postData ? e.postData.contents : "{}";
    const payload = JSON.parse(contents);
    const rows = payload.rows || (payload.row ? [payload.row] : []);

    if (!rows.length) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "error",
        message: "No rows provided"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    const sheet = getOrCreateSheet();
    const existing = getExistingKeys(sheet);
    const toAppend = [];

    for (let i = 0; i < rows.length; i++) {
      const r = rows[i];
      const email = String(r[5] || "").trim().toLowerCase();
      const linkedin = String(r[6] || "").trim().toLowerCase();
      const contactId = String(r[7] || "").trim().toLowerCase();
      const key = linkedin || email || contactId;

      if (key && existing[key]) {
        continue; // skip duplicate
      }

      if (key) existing[key] = true;
      toAppend.push(r);
    }

    if (toAppend.length > 0) {
      const startRow = sheet.getLastRow() + 1;
      sheet.getRange(startRow, 1, toAppend.length, toAppend[0].length).setValues(toAppend);
    }

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      received: rows.length,
      added: toAppend.length,
      totalRecords: sheet.getLastRow() - 1
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}
