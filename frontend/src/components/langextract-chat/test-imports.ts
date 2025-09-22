// Test import file to check if components export correctly
import ParameterOverview from './components/ParameterOverview'
import SmartSuggestions from './components/SmartSuggestions'
import XMLPreview from './components/XMLPreview'
import SourceGrounding from './components/SourceGrounding'
import { useLangExtractChat } from './hooks/useLangExtractChat'

// Test that all imports work
console.log('Imports work:', {
  ParameterOverview,
  SmartSuggestions,
  XMLPreview,
  SourceGrounding,
  useLangExtractChat
})

export { ParameterOverview, SmartSuggestions, XMLPreview, SourceGrounding, useLangExtractChat }