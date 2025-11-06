export const generateReportLink = (
  reportLink: string,
  CC: string,
  Subject: string,
  Body: string
) => {
  const userAgent = window.navigator.userAgent;
  let browserName = "Unknown";
  let osName = "Unknown";

  // Detecting browser name
  switch (true) {
    case userAgent.includes("Chrome"):
      browserName = "Chrome";
      break;
    case userAgent.includes("Firefox"):
      browserName = "Firefox";
      break;
    case userAgent.includes("Safari") && !userAgent.includes("Chrome"):
      browserName = "Safari";
      break;
    case userAgent.includes("MSIE") || userAgent.includes("Trident"):
      browserName = "Internet Explorer";
      break;
  }

  // Detecting OS name
  switch (true) {
    case userAgent.includes("Windows NT 10.0"):
      osName = "Windows 10";
      break;
    case userAgent.includes("Windows NT 6.1"):
      osName = "Windows 7";
      break;
    case userAgent.includes("Mac OS X"):
      osName = "Mac OS X";
      break;
    case userAgent.includes("Linux"):
      osName = "Linux";
      break;
  }

  const gmailLink = `https://mail.google.com/mail/?view=cm&fs=1&to=${reportLink}&cc=${encodeURIComponent(
    CC
  )}&su=${encodeURIComponent(Subject)}&body=${encodeURIComponent(
    Body +
      `

Please leave this information as it is: 
- User Agent: ${userAgent}
- Browser: ${browserName}
- OS: ${osName}`
  )}`;

  return gmailLink;
};
