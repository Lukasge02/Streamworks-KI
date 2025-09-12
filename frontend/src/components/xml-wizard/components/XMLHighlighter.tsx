/**
 * XMLHighlighter - Syntax highlighting with placeholder emphasis
 */
'use client'

import React from 'react'

interface XMLHighlighterProps {
  xmlContent: string
  className?: string
  showLineNumbers?: boolean
  highlightPlaceholders?: boolean
}

export const XMLHighlighter: React.FC<XMLHighlighterProps> = ({
  xmlContent,
  className = '',
  showLineNumbers = true,
  highlightPlaceholders = true
}) => {
  const highlightXML = (content: string) => {
    if (!content) return []
    
    const lines = content.split('\n')
    
    return lines.map((line, lineIndex) => {
      // Split line into parts for highlighting
      let parts: Array<{ text: string; type: 'text' | 'tag' | 'attribute' | 'value' | 'placeholder' | 'comment' }> = []
      let currentIndex = 0
      
      // XML comment regex
      const commentRegex = /<!--[\s\S]*?-->/g
      let commentMatch
      while ((commentMatch = commentRegex.exec(line)) !== null) {
        if (commentMatch.index > currentIndex) {
          parts.push({ text: line.substring(currentIndex, commentMatch.index), type: 'text' })
        }
        parts.push({ text: commentMatch[0], type: 'comment' })
        currentIndex = commentMatch.index + commentMatch[0].length
      }
      
      if (currentIndex < line.length) {
        const remainingLine = line.substring(currentIndex)
        
        // Placeholder regex - highlight {{...}}
        if (highlightPlaceholders) {
          const placeholderRegex = /\{\{[^}]+\}\}/g
          let lastIndex = 0
          let placeholderMatch
          
          while ((placeholderMatch = placeholderRegex.exec(remainingLine)) !== null) {
            if (placeholderMatch.index > lastIndex) {
              parts.push({ 
                text: remainingLine.substring(lastIndex, placeholderMatch.index), 
                type: 'text' 
              })
            }
            parts.push({ 
              text: placeholderMatch[0], 
              type: 'placeholder' 
            })
            lastIndex = placeholderMatch.index + placeholderMatch[0].length
          }
          
          if (lastIndex < remainingLine.length) {
            parts.push({ 
              text: remainingLine.substring(lastIndex), 
              type: 'text' 
            })
          }
        } else {
          parts.push({ text: remainingLine, type: 'text' })
        }
      }
      
      // Further process non-placeholder parts for XML syntax highlighting
      const processedParts = parts.flatMap(part => {
        if (part.type !== 'text') {
          return [part]
        }
        
        return highlightXMLSyntax(part.text)
      })
      
      return {
        lineNumber: lineIndex + 1,
        parts: processedParts
      }
    })
  }
  
  const highlightXMLSyntax = (text: string) => {
    const parts: Array<{ text: string; type: 'text' | 'tag' | 'attribute' | 'value' | 'placeholder' | 'comment' }> = []
    
    // Simple XML tag regex
    const xmlRegex = /<\/?[^>]+>/g
    let lastIndex = 0
    let match
    
    while ((match = xmlRegex.exec(text)) !== null) {
      // Add text before tag
      if (match.index > lastIndex) {
        parts.push({
          text: text.substring(lastIndex, match.index),
          type: 'text'
        })
      }
      
      // Add the tag
      parts.push({
        text: match[0],
        type: 'tag'
      })
      
      lastIndex = match.index + match[0].length
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push({
        text: text.substring(lastIndex),
        type: 'text'
      })
    }
    
    return parts
  }
  
  const getPartClassName = (type: string) => {
    switch (type) {
      case 'tag':
        return 'text-blue-600 dark:text-blue-400'
      case 'attribute':
        return 'text-green-600 dark:text-green-400'
      case 'value':
        return 'text-orange-600 dark:text-orange-400'
      case 'placeholder':
        return 'bg-yellow-200 dark:bg-yellow-800/50 text-yellow-800 dark:text-yellow-200 px-1 rounded font-medium'
      case 'comment':
        return 'text-gray-500 dark:text-gray-400 italic'
      default:
        return 'text-gray-800 dark:text-gray-200'
    }
  }
  
  const highlightedLines = highlightXML(xmlContent)
  
  return (
    <div className={`font-mono text-sm overflow-x-auto ${className}`}>
      <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
        {highlightedLines.map((line, index) => (
          <div 
            key={index}
            className="flex border-b border-gray-100 dark:border-gray-700 last:border-b-0 hover:bg-gray-100 dark:hover:bg-gray-700/50"
          >
            {showLineNumbers && (
              <div className="flex-shrink-0 w-12 px-3 py-2 text-gray-400 dark:text-gray-500 text-right border-r border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-800/50">
                {line.lineNumber}
              </div>
            )}
            <div className="flex-1 px-4 py-2 whitespace-pre-wrap break-all">
              {line.parts.map((part, partIndex) => (
                <span 
                  key={partIndex}
                  className={getPartClassName(part.type)}
                >
                  {part.text}
                </span>
              ))}
            </div>
          </div>
        ))}
        
        {highlightedLines.length === 0 && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <div className="space-y-2">
              <div className="text-2xl">📄</div>
              <p>XML wird generiert...</p>
              <p className="text-sm">Füllen Sie den Wizard aus, um eine Vorschau zu sehen</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default XMLHighlighter