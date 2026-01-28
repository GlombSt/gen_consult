# Prompt Builder Frontend Structure

Based on the GenPlus - Declarative Prompt Builder UI, here's where this feature should live in the frontend codebase.

## Feature Location

```
customer-ux/src/features/prompt-builder/
```

## Component Hierarchy

### Main Entry Point
**Location:** `customer-ux/src/features/prompt-builder/components/PromptBuilder/PromptBuilder.jsx`

This is the main container component that orchestrates the three-column layout:
- Header bar
- Declarations column (left)
- Output Preview column (center)
- Consultant column (right)

### Component Structure

```
customer-ux/src/features/prompt-builder/
├── components/
│   ├── PromptBuilder/
│   │   ├── PromptBuilder.jsx          # Main container (3-column layout)
│   │   ├── PromptBuilder.css          # Main styles
│   │   └── Header/
│   │       ├── Header.jsx             # Top bar with title and action buttons
│   │       └── Header.css
│   │
│   ├── Declarations/
│   │   ├── Declarations.jsx           # Left column container
│   │   ├── Declarations.css
│   │   ├── IntentSection/
│   │   │   ├── IntentSection.jsx      # Intent textarea with label
│   │   │   └── IntentSection.css
│   │   ├── FactsSection/
│   │   │   ├── FactsSection.jsx       # Facts input with "Add" button
│   │   │   ├── FactsSection.css
│   │   │   └── FactItem/              # Individual fact item component
│   │   │       ├── FactItem.jsx
│   │   │       └── FactItem.css
│   │   ├── ConstraintsSection/
│   │   │   ├── ConstraintsSection.jsx # Constraints with quick-add buttons
│   │   │   ├── ConstraintsSection.css
│   │   │   └── ConstraintItem/        # Individual constraint component
│   │   │       ├── ConstraintItem.jsx
│   │   │       └── ConstraintItem.css
│   │   ├── OutputStructureSection/
│   │   │   ├── OutputStructureSection.jsx # Sections list with add/order controls
│   │   │   └── OutputStructureSection.css
│   │   ├── OutputFormatSection/
│   │   │   ├── OutputFormatSection.jsx # Format dropdown (Markdown, etc.)
│   │   │   └── OutputFormatSection.css
│   │   └── SampleOutputSection/
│   │       ├── SampleOutputSection.jsx # Optional sample output textarea
│   │       └── SampleOutputSection.css
│   │
│   ├── OutputPreview/
│   │   ├── OutputPreview.jsx          # Center column container
│   │   ├── OutputPreview.css
│   │   ├── PreviewArea/
│   │   │   ├── PreviewArea.jsx        # Output preview textarea
│   │   │   └── PreviewArea.css
│   │   ├── Annotations/
│   │   │   ├── Annotations.jsx        # Annotation buttons (Too verbose, etc.)
│   │   │   └── Annotations.css
│   │   └── PromptDisplay/
│   │       ├── PromptDisplay.jsx      # Auto-generated prompt display
│   │       └── PromptDisplay.css
│   │
│   └── Consultant/
│       ├── Consultant.jsx             # Right column chat interface
│       ├── Consultant.css
│       ├── ChatInput/
│       │   ├── ChatInput.jsx          # Input field with Send button
│       │   └── ChatInput.css
│       └── ChatTips/
│           ├── ChatTips.jsx           # Tips section (/suggest, /summarize, /template)
│           └── ChatTips.css
│
├── hooks/
│   ├── usePromptBuilder.js           # Main state management hook
│   ├── useDeclarations.js            # Declarations state logic
│   ├── useOutputPreview.js           # Preview generation logic
│   ├── useConsultant.js              # Consultant chat logic
│   └── usePromptGeneration.js        # Auto-generate prompt from declarations
│
├── api/
│   ├── promptBuilderApi.js           # API calls for saving/loading prompts
│   └── consultantApi.js              # API calls for consultant chat
│
└── utils/
    ├── promptGenerator.js            # Logic to generate prompt from declarations
    ├── formatHelpers.js              # Output formatting utilities
    └── validation.js                # Declaration validation logic
```

## Integration Points

### App.jsx Update
Replace the current content with:

```jsx
import PromptBuilder from './features/prompt-builder/components/PromptBuilder/PromptBuilder'
import './App.css'

function App() {
  return (
    <div className="app">
      <PromptBuilder />
    </div>
  )
}
```

### Routing Consideration
If you plan to have multiple views later, consider:
- `customer-ux/src/pages/PromptBuilderPage.jsx` → wraps `PromptBuilder` component
- Use React Router if needed for navigation

## Shared Components

Components that might be reused across features:

```
customer-ux/src/shared/
├── components/
│   ├── Button/                       # Standardized button component
│   ├── Textarea/                     # Enhanced textarea with labels
│   ├── Input/                        # Enhanced input with labels
│   ├── Dropdown/                     # Dropdown/select component
│   └── Layout/
│       └── ThreeColumnLayout.jsx     # Reusable 3-column layout wrapper
│
└── hooks/
    ├── useKeyboardShortcut.js       # For ⌘/Ctrl + Enter handling
    └── useAutoRefresh.js            # Auto-refresh logic
```

## State Management

### Recommended Approach
Use React Context + custom hooks for state management:

```
customer-ux/src/features/prompt-builder/
└── context/
    └── PromptBuilderContext.jsx     # Shared state for all prompt builder components
```

### State Structure Example
```javascript
{
  declarations: {
    intent: '',
    facts: [],
    constraints: [],
    outputStructure: [],
    outputFormat: 'markdown',
    sampleOutput: ''
  },
  output: {
    preview: '',
    prompt: ''
  },
  consultant: {
    messages: [],
    loading: false
  },
  settings: {
    autoRefresh: true
  }
}
```

## Styling Strategy

1. **Component-level CSS**: Each component has its own `.css` file
2. **Global styles**: Update `customer-ux/src/index.css` for dark theme foundation
3. **CSS Variables**: Define theme variables in `index.css`:
   ```css
   :root {
     --bg-primary: #1a1a1a;
     --bg-secondary: #2d2d2d;
     --text-primary: #ffffff;
     --accent-blue: #3b82f6;
     /* etc. */
   }
   ```

## File Naming Convention

Following the existing pattern from `items` feature:
- Component files: `ComponentName.jsx` (PascalCase)
- CSS files: `ComponentName.css` (matching component name)
- Hook files: `useHookName.js` (camelCase with 'use' prefix)
- API files: `featureApi.js` (camelCase with 'Api' suffix)

