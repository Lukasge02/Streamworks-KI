/**
 * ChapterNavigation Component
 * Advanced navigation with expandable chapters and sub-chapters
 */
'use client'

import React from 'react'
import { WizardChapter, SubChapter } from '../types/wizard.types'
import { Button } from '@/components/ui/button'
import { 
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Circle,
  AlertTriangle,
  Clock,
  FileText,
  Settings,
  Play,
  Target,
  Monitor
} from 'lucide-react'

interface ChapterNavigationProps {
  chapters: WizardChapter[]
  currentChapter: string
  currentSubChapter: string
  onChapterClick: (chapterId: string) => void
  onSubChapterClick: (chapterId: string, subChapterId: string) => void
  onToggleChapter: (chapterId: string) => void
}

const CHAPTER_ICONS = {
  'stream-properties': Settings,
  'job-configuration': Play,
  'scheduling': Clock,
  'review': Target
}

const getSubChapterIcon = (subChapter: SubChapter) => {
  if (subChapter.hasErrors) return AlertTriangle
  if (subChapter.isCompleted) return CheckCircle2
  if (subChapter.isValid) return CheckCircle2
  return Circle
}

const getSubChapterColor = (subChapter: SubChapter, isCurrent: boolean) => {
  if (isCurrent) {
    return 'text-blue-600 dark:text-blue-400'
  }
  if (subChapter.hasErrors) {
    return 'text-red-600 dark:text-red-400'
  }
  if (subChapter.isCompleted) {
    return 'text-green-600 dark:text-green-400'
  }
  if (subChapter.isValid) {
    return 'text-green-600 dark:text-green-400'
  }
  return 'text-gray-400 dark:text-gray-500'
}

export const ChapterNavigation: React.FC<ChapterNavigationProps> = ({
  chapters,
  currentChapter,
  currentSubChapter,
  onChapterClick,
  onSubChapterClick,
  onToggleChapter
}) => {
  return (
    <div className="space-y-2">
      {chapters.map((chapter) => {
        const IconComponent = CHAPTER_ICONS[chapter.id as keyof typeof CHAPTER_ICONS] || FileText
        const isCurrentChapter = chapter.id === currentChapter
        const isExpanded = chapter.isExpanded
        
        return (
          <div key={chapter.id} className="space-y-1">
            {/* Chapter Header */}
            <div
              className={`flex items-center justify-between p-3 rounded-lg transition-all duration-200 border ${
                isCurrentChapter
                  ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700'
                  : chapter.isCompleted
                  ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-700'
                  : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
            >
              {/* Clickable area for chapter navigation */}
              <div 
                className="flex items-center space-x-3 flex-1 cursor-pointer"
                onClick={() => onChapterClick(chapter.id)}
                title={`Zu ${chapter.title} Übersicht`}
              >
                {/* Chapter Icon */}
                <div className={`flex-shrink-0 p-1 rounded ${
                  isCurrentChapter
                    ? 'bg-blue-100 dark:bg-blue-800/50'
                    : chapter.isCompleted
                    ? 'bg-green-100 dark:bg-green-800/50'
                    : 'bg-gray-100 dark:bg-gray-700'
                }`}>
                  <IconComponent className={`w-4 h-4 ${
                    isCurrentChapter
                      ? 'text-blue-600 dark:text-blue-400'
                      : chapter.isCompleted
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                </div>
                
                {/* Chapter Info */}
                <div className="flex-1 min-w-0">
                  <h3 className={`font-medium text-sm ${
                    isCurrentChapter
                      ? 'text-blue-900 dark:text-blue-100'
                      : chapter.isCompleted
                      ? 'text-green-900 dark:text-green-100'
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {chapter.title}
                  </h3>
                </div>
              </div>

              {/* Expand/Collapse Icon */}
              <div 
                className="flex items-center space-x-2 cursor-pointer p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                onClick={(e) => {
                  e.stopPropagation() // Prevent chapter navigation
                  onToggleChapter(chapter.id)
                }}
                title={isExpanded ? "Kapitel zuklappen" : "Kapitel aufklappen"}
              >
                {/* Completion Status */}
                {chapter.isCompleted && (
                  <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                )}
                
                {/* Expand/Collapse */}
                {isExpanded ? (
                  <ChevronDown className={`w-4 h-4 ${
                    isCurrentChapter
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-400 dark:text-gray-500'
                  }`} />
                ) : (
                  <ChevronRight className={`w-4 h-4 ${
                    isCurrentChapter
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-400 dark:text-gray-500'
                  }`} />
                )}
              </div>
            </div>

            {/* Sub-Chapters */}
            {isExpanded && chapter.subChapters.length > 0 && (
              <div className="ml-6 space-y-1">
                {chapter.subChapters.map((subChapter) => {
                  const isCurrentSubChapter = chapter.id === currentChapter && 
                                             subChapter.id === currentSubChapter
                  const SubIcon = getSubChapterIcon(subChapter)
                  const iconColor = getSubChapterColor(subChapter, isCurrentSubChapter)
                  
                  return (
                    <div
                      key={subChapter.id}
                      className={`flex items-center space-x-3 p-2 rounded-md cursor-pointer transition-all duration-150 ${
                        isCurrentSubChapter
                          ? 'bg-blue-100 dark:bg-blue-900/30'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700/50'
                      }`}
                      onClick={() => onSubChapterClick(chapter.id, subChapter.id)}
                    >
                      {/* Sub-Chapter Icon */}
                      <SubIcon className={`w-3.5 h-3.5 ${iconColor}`} />
                      
                      {/* Sub-Chapter Info */}
                      <div className="flex-1 min-w-0">
                        <h4 className={`text-sm font-medium ${
                          isCurrentSubChapter
                            ? 'text-blue-900 dark:text-blue-100'
                            : 'text-gray-700 dark:text-gray-200'
                        }`}>
                          {subChapter.title}
                        </h4>
                        
                        {/* Validation Message */}
                        {subChapter.validationMessage && (
                          <p className={`text-xs mt-1 ${
                            subChapter.hasErrors
                              ? 'text-red-600 dark:text-red-400'
                              : 'text-green-600 dark:text-green-400'
                          }`}>
                            {subChapter.validationMessage}
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default ChapterNavigation