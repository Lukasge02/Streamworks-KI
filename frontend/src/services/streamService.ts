import { StreamConfig } from '../types';

export class StreamService {
  static validateStreamConfig(config: StreamConfig): string[] {
    const errors: string[] = [];
    
    if (!config.streamName.trim()) {
      errors.push('Stream Name ist erforderlich');
    }
    if (!config.jobName.trim()) {
      errors.push('Job Name ist erforderlich');
    }
    if (!config.dataSource.trim()) {
      errors.push('Data Source ist erforderlich');
    }
    
    return errors;
  }

  static generateXmlFromConfig(config: StreamConfig): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<stream>
  <n>${config.streamName}</n>
  <job>
    <n>${config.jobName}</n>
    <startTime>${config.startTime}</startTime>
    <dataSource>${config.dataSource}</dataSource>
    <outputPath>${config.outputPath}</outputPath>
    <schedule>${config.schedule}</schedule>
  </job>
</stream>`;
  }

  static downloadXmlFile(content: string, filename: string): void {
    const blob = new Blob([content], { type: 'text/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}