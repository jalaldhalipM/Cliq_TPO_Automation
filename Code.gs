const CLIQ_WEBHOOK_URL = "https://cliq.zoho.com/company/902162992/api/v2/channelsbyname/tpoleads/message";
// Note: If you have a zapikey, append it to the URL above, like:
// const CLIQ_WEBHOOK_URL = "https://cliq.zoho.com/company/902162992/api/v2/channelsbyname/tpoleads/message?zapikey=YOUR_TOKEN_HERE";

/**
 * Triggered automatically when a user submits a Google Form linked to this sheet.
 */
function onFormSubmit(e) {
  try {
    var namedValues = e.namedValues;
    
    // Extract values based on column headers. 
    // Fallback to "N/A" if the column is missing or empty.
    var fullName = namedValues["full_name"] ? namedValues["full_name"][0] : "N/A";
    var phone = namedValues["phone_number"] ? namedValues["phone_number"][0] : "N/A";
    var email = namedValues["email"] ? namedValues["email"][0] : "N/A";
    var designation = namedValues["designation"] ? namedValues["designation"][0] : "N/A";
    var challenge = namedValues["what_is_your_current_placement_challenge?"] ? namedValues["what_is_your_current_placement_challenge?"][0] : "N/A";
    var college = namedValues["college_/_institution_name"] ? namedValues["college_/_institution_name"][0] : "N/A";

    sendToCliq(fullName, phone, email, designation, challenge, college);
  } catch (error) {
    Logger.log("Error in onFormSubmit: " + error.toString());
  }
}

/**
 * Helper function to send the payload to Zoho Cliq.
 */
function sendToCliq(fullName, phone, email, designation, challenge, college) {
  var message = "🚀 *New Lead Received*\n\n" +
                "*Name:* " + fullName + "\n" +
                "*Phone:* " + phone + "\n" +
                "*Email:* " + email + "\n" +
                "*Designation:* " + designation + "\n" +
                "*College/Institution:* " + college + "\n" +
                "*Challenge:* " + challenge;
                
  var payload = {
    "text": message,
    "bot": {
      "name": "Lead Automation Bot",
      "image": "https://cdn-icons-png.flaticon.com/512/4144/4144673.png"
    }
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(CLIQ_WEBHOOK_URL, options);
  Logger.log(response.getContentText());
}

/**
 * Custom Menu for manual testing.
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Lead Automation')
      .addItem('Send Last Row to Cliq (Test)', 'testSendLastRow')
      .addToUi();
}

/**
 * Reads the last row in the sheet and sends it to Cliq for testing purposes.
 */
function testSendLastRow() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  
  if (lastRow <= 1) {
    SpreadsheetApp.getUi().alert("No data found to send.");
    return;
  }
  
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var lastRowData = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  var dataMap = {};
  for (var i = 0; i < headers.length; i++) {
    var headerStr = headers[i].toString().trim();
    dataMap[headerStr] = lastRowData[i];
  }
  
  var fullName = dataMap["full_name"] || "N/A";
  var phone = dataMap["phone_number"] || "N/A";
  var email = dataMap["email"] || "N/A";
  var designation = dataMap["designation"] || "N/A";
  var challenge = dataMap["what_is_your_current_placement_challenge?"] || "N/A";
  var college = dataMap["college_/_institution_name"] || "N/A";
  
  sendToCliq(fullName, phone, email, designation, challenge, college);
  SpreadsheetApp.getUi().alert("Test message sent! Check Zoho Cliq.");
}
