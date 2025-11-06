import { format, parseISO } from "date-fns";

export class CalculationsUtil {
  static countWords(text: string): number {
    if (!text) {
      return 0;
    }
    return text
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0).length;
  }

  static formatTime(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);

    const formattedMinutes = String(minutes).padStart(2, "0");
    const formattedSeconds = String(remainingSeconds).padStart(2, "0");

    return `${formattedMinutes}:${formattedSeconds}`;
  }

  static formatDateTime(isoString: string) {
    const date = parseISO(isoString);

    const formattedDate = format(date, "dd/MM/yyyy 'at' h:mmaaa");
    return formattedDate;
  }

  static generate12DigitRandomId(): number {
    const minNum = Math.pow(10, 11);
    const maxNum = Math.pow(10, 12) - 1;
    return Math.floor(Math.random() * (maxNum - minNum + 1)) + minNum;
  }
}
