export class FormatUtils {
  static formatTimestamp(date: Date): string {
    return date.toLocaleTimeString();
  }

  static copyToClipboard(text: string): Promise<void> {
    return navigator.clipboard.writeText(text);
  }

  static generateMessageId(): string {
    return Date.now().toString();
  }

  static isXmlContent(text: string): boolean {
    return text.trim().startsWith('<?xml') || text.includes('<stream>');
  }
}