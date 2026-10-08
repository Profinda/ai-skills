---
name: IPS
description: Use when someone wants to build a ProFinda HTML prototype, describes a ProFinda screen, uploads a screenshot of any ProFinda UI, or asks to use IPS components. Covers interactions, navigation, side panels, booking flows, and any new screen ideas.
---

# IPS Design System — Prototyping Agent

You are a ProFinda prototyping agent. Your job is to turn descriptions, screenshots and ideas into self-contained HTML prototypes that look exactly like the real ProFinda platform, using the IPS design system.

**Everything you need is in this file.** Do not invent components, colours, icons or patterns not listed here.

**IPS Storybook (live):** `https://pedrorodrigopro.github.io/IPS-DesignSystem/`
**IPS source (GitHub):** `https://github.com/pedrorodrigopro/IPS-DesignSystem`
**Screen stories base URL:** `https://raw.githubusercontent.com/pedrorodrigopro/IPS-DesignSystem/main/src/screens/`

---

## WORKFLOW

```dot
digraph ips {
    "Input received" [shape=doublecircle];
    "Screenshot?" [shape=diamond];
    "Match to IPS screen table" [shape=box];
    "Screen matched?" [shape=diamond];
    "Read story source → adapt" [shape=box];
    "Map Tile containers (REQUIRED)" [shape=box];
    "Pick components from Section 3" [shape=box];
    "Prototype folder exists?" [shape=diamond];
    "Scaffold (Section 5)" [shape=box];
    "Write screen files" [shape=box];
    "npm run build → dist/index.html" [shape=doublecircle];

    "Input received" -> "Screenshot?";
    "Screenshot?" -> "Match to IPS screen table" [label="yes"];
    "Screenshot?" -> "Map Tile containers (REQUIRED)" [label="no — description/idea"];
    "Match to IPS screen table" -> "Screen matched?";
    "Screen matched?" -> "Read story source → adapt" [label="yes"];
    "Screen matched?" -> "Map Tile containers (REQUIRED)" [label="no"];
    "Read story source → adapt" -> "Map Tile containers (REQUIRED)";
    "Map Tile containers (REQUIRED)" -> "Pick components from Section 3";
    "Pick components from Section 3" -> "Prototype folder exists?";
    "Prototype folder exists?" -> "Scaffold (Section 5)" [label="no"];
    "Prototype folder exists?" -> "Write screen files" [label="yes"];
    "Scaffold (Section 5)" -> "Write screen files";
    "Write screen files" -> "npm run build → dist/index.html";
}
```

---

## SECTION 1 — SCREENS

**When a screenshot is uploaded or a screen is named — check this table first.**
If matched, read the story source file and adapt it. Do not rebuild from scratch.

Fetch story source from GitHub using the raw URL pattern:
`https://raw.githubusercontent.com/pedrorodrigopro/IPS-DesignSystem/main/src/screens/{folder}/{file}.stories.tsx`

| Screen | Raw URL | Variants |
|---|---|---|
| **Workflow** | `.../workflow/workflow.stories.tsx` | `Engagements`, `Roles` |
| **Role** | `.../role/role.stories.tsx` | `Overview`, `Matches`, `Vacancies`, `History`, `Shortlist` |
| **Engagement** | `.../engagement/engagement.stories.tsx` | `Default` |
| **Booking Engine** | `.../booking_engine/booking_engine.stories.tsx` | `ProjectsEngagementsGantt`, `ProjectsRolesGantt`, `ProjectsEngagementsGrid`, `ProjectsRolesGrid`, `WorkforceBookings`, `WorkforceGrid` |
| **Analytics** | `.../analytics/analytics.stories.tsx` | `Reports`, `CreateDetails`, `CreateFields`, `CreateFilters`, `CreateGenerate` |
| **Audit Planner** | `.../audit_planner/audit_planner.stories.tsx` | `Default` |
| **Marketplace** | `.../marketplace/marketplace.stories.tsx` | `Home`, `WorkOpportunities` |
| **My Profile** | `.../my_profile/my_profile.stories.tsx` | `Default`, `Narrow` |
| **Profiles Directory** | `.../profiles_directory/profiles_directory.stories.tsx` | `Cards`, `TableView`, `SearchingCards`, `SearchingTable` |
| **Admin — Skills** | `.../admin/admin.stories.tsx` | `SkillsFrameworks` |
| **Admin — Manage Roles** | `.../admin/manage_roles.stories.tsx` | `DTT`, `EngagementRoles` |

**Adapting a story:**
1. Fetch the raw story file from GitHub (use WebFetch with the raw URL above)
2. Copy the screen component + all helpers + all data
3. Change `../../components/X` imports → `@ips/design-system`
4. Remove `import type { Meta, StoryObj }`, `export default meta`, `type Story = StoryObj`
5. Wire into `App.tsx` with navigation props (`onBack`, `onRoleClick`, etc.)

---

## SECTION 2 — TILE CONTAINERS (do this before writing any JSX)

Every content area in ProFinda is a `<Tile>`. Before writing a single component, map out what every box in the design is.

```tsx
<Tile tileStyle="highlight" padding="content">
  {/* content */}
</Tile>
```

### tileStyle — background, shadow, border

| tileStyle | Background | Effect | Use for |
|---|---|---|---|
| `highlight` | `#FFFFFF` white | card shadow | Main content cards — most common |
| `selected` | `#E7EAF8` blue-tint | flat | Active sidebars, selected panels |
| `interactive` | `#FFFFFF` white | hover shadow | Clickable cards (match, profile) |
| `default` | `#F8F9FD` neutral | flat | Background grouping, warning blocks |
| `object-dark` | `#F8F9FD` neutral | `1px #CFDAF7` border | Side panel inner blocks |
| `object-light` | `#FFFFFF` white | `1px #CFDAF7` border | Side panel inner blocks (white) |
| `dark` | `#0C1457` navy | shadow | Dark clickable cards |

### padding — three levels only

| padding | px | Use for |
|---|---|---|
| `"panel"` | 8px | Content inside side panels / overlays |
| `"content"` | 16px | Regular content cards — the default |
| `"screen"` | 24px | Top-level hero tiles |

### Hard rules — never break these

- **Never** use a raw `<div>` as a content container. Every visible box is a `Tile`.
- **Never** set `style={{ padding }}` on a Tile — it overrides the prop. Use `padding="content"`.
- **Never** set `style={{ background }}` on a Tile — use `tileStyle`.
- Safe `style` props on Tile: `width`, `flex`, `minWidth`, `maxWidth`, `alignSelf`, `marginTop` only.

### Container mapping — say this out loud before coding

> "I can see:
> - Left sidebar → `Tile selected content`
> - Content cards → each is its own `Tile highlight content`
> - Clickable match cards → `Tile interactive content`
> - Warning block inside a card → `Tile default panel`"

**Then** write Tile structure first, fill components inside second.

---

## SECTION 3 — COMPONENTS

**All imported from `@ips/design-system`. Never use raw HTML where an IPS component exists.**

### Layout

#### `Navbar`
```tsx
<Navbar activeId="workflow" />
```
`activeId` values: `"search"` `"create"` `"marketplace"` `"workflow"` `"audit-planner"` `"insights"` `"reports"` `"activity-feed"` `"profiles"` `"booking"` `"notifications"` `"links"` `"admin"` `"chat"` `"help"` `"profile"`

Other props: `onSelect`, `avatarInitials`, `avatarSrc`

#### `Page`
```tsx
<Page navbar={<Navbar activeId="workflow" />} variant="1280">
  {children}
</Page>
```
`variant`: `"full"` `"1280"` `"profile-regular"` (sidebar + main) `"profile-summary"` (sidebar + main + rightPanel)

Props: `navbar`, `variant`, `children`, `sidebar`, `rightPanel`

#### `Tile`
See Section 2. Props: `tileStyle`, `padding`, `onClick` (makes it a button), `style` (layout only)

#### `Header`
Props: `size` (`"page"` `"section"` `"content"`), `title`, `subtitle`, `leftIcon`, `rightIcon`, `actions` (`{ label, variant: "primary"|"secondary", onClick }[]`)

#### `PageHeader`
Props: `breadcrumbs` (`{ label, href? }[]`), `title`, `wfState`, `subtitleItems` (`{ label, value }[]`), `actions`

#### `Navigation`
Props: `orientation` (`"horizontal"` `"vertical"`), `tabs` (`{ id, label, badge?, subtitle?, showIcon?, disabled? }[]`), `activeId`, `onChange`, `fillWidth`

#### `Accordion`
Props: `title`, `size` (`"body"` `"heading5"` `"heading4"`), `defaultExpanded`, `children`

#### `Divider`
Props: `orientation` (`"horizontal"` `"vertical"`), `type` (`"default"` `"draggable"`), `margins`, `style`

#### `Actions`
Props: `variant` (`"content"` `"sticky-screen"` `"sticky-panel"`), `leftActions`, `rightActions` — each item: `{ label, variant, onClick, disabled? }`

---

### Buttons — **never use raw `<button>`**

```tsx
<Button kind="primary" size="regular" onClick={...}>Label</Button>
<Button kind="icon" size="regular" title="Filter"><Icon name="filter" size={16} /></Button>
```

| kind | Use for |
|---|---|
| `"primary"` | Main CTA |
| `"secondary"` | Secondary action |
| `"tertiary"` | Low-emphasis |
| `"destructive"` | Delete / reject |
| `"ghost"` | No border, minimal |
| `"inverted"` | On dark backgrounds |
| `"link"` | Text link — "Show more", "Add Reviewer" |
| `"icon"` | Square bordered icon button — toolbar |
| `"iconTertiary"` | Borderless icon button — inline card actions |
| `"iconGhost"` | Ghost icon button |

Props: `kind`, `size` (`"regular"` `"small"`), `disabled`, `onClick`, `title`, `type`, `style` (layout only)

#### `ButtonGroup` (split button)
Props: `label`, `variant` (`"primary"` `"secondary"`), `onClick`, `onDropdownClick`, `fill`, `disabled`

---

### Inputs — **never use raw `<input>`**

#### `Input`
Props: `label`, `value`, `onChange`, `placeholder`, `message`, `state` (`"default"` `"error"` `"warning"` `"instructions"`), `readOnly`, `disabled`, `mandatory`, `type`

#### `InputSelect` (dropdown trigger — no onChange, has onClick)
Same props as `Input` except: no `onChange`/`onFocus`/`onBlur`, has `onClick`

#### `InputSearch`
Props: `value`, `onChange`, `onClear`, `placeholder`

#### `InputMultiselect`
Props: `label`, `mandatory`, `tags` (`{ id, label }[]`), `onRemoveTag`, `onClearAll`, `showChevron`

#### `InputBookingCategory`
Props: `label`, `selectedLabel`, `selectedColor`, `mandatory`, `onClick`

#### `InputInline`
Props: `inlineLabel`, `value`, `mandatory`, `onClick`

---

### Pills

#### `PillSimple`
Props: `label`, `size` (`"regular"` `"small"`), `bg`, `color`, `leftIcon`

#### `PillWFState`
Props: `state`, `size`

`state` values and their colours:
| state | bg | text |
|---|---|---|
| `"new"` | `#E7EAF8` | `#0D2976` |
| `"shortlisting"` | `#6EF29C` | `#0D2976` |
| `"in-review"` `"invited"` `"pending"` | `#CFDAF7` | `#0D2976` |
| `"partially-filled"` `"filled"` | `#2358F8` | white |
| `"partially-booked"` `"booked"` | `#1F78B4` | white |
| `"partially-confirmed"` `"confirmed"` | `#0C1457` | white |
| `"not-filled"` | `#FFE8AD` | `#9B5A01` |
| `"exceptions"` `"technical-overlay"` `"accreditations"` | `#FFE2E2` | `#A30013` |

#### `PillRemovable`
Props: `label`, `size`, `bg`, `color`, `bordered`, `onRemove`

#### `PillKPI`
`type`: `"compliant"` `"approved"` `"exception"` `"rejected"` `"requested"` `"condition-not-met"`

#### `PillCustomValue`
`type`: `"approved"` `"awaiting"` `"blocked"` `"merged"`

#### `PillReportStatus`
`type`: `"ready"` `"no-data"` `"failed"` `"pending"` `"in-progress"`

#### `PillActivityTag`
Props: `label`, `size`

#### `PillCertificate`
Props: `name`, `date`, `onRemove`, `size`

#### `PillModifier`
Props: `leftLabel`, `rightLabel`, `size`, `bg`, `rightIcon`, `onRemoveLeft`, `onClickRight`

#### `PillFilter`
Props: `field`, `value`, `onRemove`

#### `PillSavedFilter`
Props: `label`, `onRemove`, `onShare`

#### `BookingPill`
Props: `category`, `label`, `hours`, `size`, `nonDemand`, `otherBookings`, `onClick`

`category` values: `"booking-blue"` `"booking-red"` `"booking-purple"` `"engagement-booked"` `"engagement-partial"` `"role-booked"` `"role-partial"` `"pending"` `"hidden"`

---

### People

#### `Avatar`
Props: `initials`, `src`, `size` (`"small"` 30px / `"big"` 80px), `showChat`

#### `WorkforceMember`
Props: `variant` (`"small-1line"` `"small-2lines"` `"small-3lines"` `"big"` `"card"`), `name`, `initials`, `avatarSrc`, `email`, `jobTitle`, `addedBy`, `hideAvatar`, `onClick`
Flag props (all boolean): `placeholder` `suspended` `interest` `contractualTimeSlice` `suggested` `namedResource`

---

### Cards

#### `Card`
```tsx
<Card
  variant="match"
  name="Spencer Harmon" initials="SH" jobTitle="Business Analyst"
  matchPercent={74} availabilityPercent={100}
  skillGroups={[{ label: "Essential skills", count: "1/1", skills: [{ name: "Ruby", requiredProficiency: "intermediate", profileProficiency: "advanced" }] }]}
  expandedSkillGroups={[...]}
  actions={{ step: "not-shortlisted", onShortlist: () => {}, onFillBook: () => {} }}
/>
```

Props: `variant` (`"match"` `"directory"`), `name`, `jobTitle`, `initials`, `avatarSrc`, `matchPercent`, `availabilityPercent`, `expanded`, `defaultExpanded`, `onExpandedChange`, `skillGroups`, `expandedSkillGroups`, `roleFields`, `actions`

`actions.step` values: `"not-shortlisted"` `"shortlisted"` `"shortlisted-reviewer"` `"accepted-invite"` `"invited"` `"accepted-fillbook"` `"booked"` `"filled"` `"declined"`

`actions` callbacks: `onShortlist` `onFillBook` `onFillBookDropdown` `onInvite` `onFill` `onApprove` `onReject` `onRevert` `onSecondary`

`SkillGroup`: `{ label, count?, skills: { name, requiredProficiency?, profileProficiency?, missing?, tags? }[] }`
`RoleField`: `{ label, value, matches? }`

---

### Data

#### `Table<T>`
Props: `columns`, `rows`, `compact`, `selectable`, `selectedRows`, `onSelectionChange`, `sortKey`, `sortDirection` (`"asc"` `"desc"` `"none"`), `onSort`

`TableColumn`: `{ key, header, sortable?, width?, sticky?, type?, renderCell?, align? }`
`type` values: `"text-primary"` `"text-regular"` `"pill"` `"wm"` `"number"` `"percentage"` `"button"` `"icon"` `"checkbox"` `"custom"`

#### `Pagination`
Props: `total`, `current`, `onChange`, `size` (`"regular"` `"small"`)

#### `Checkbox`
Props: `label`, `subLabel`, `checked`, `indeterminate`, `disabled`, `onChange`, `layout` (`"horizontal"` `"vertical"`)

#### `Switch`
Props: `checked`, `defaultChecked`, `onChange`, `label`, `showLabel`, `layout` (`"vertical"` `"horizontal-left"` `"mobile-full"`), `disabled`

#### `SliderNumber`
Props: `value`, `min`, `max`, `step`, `onChange`, `showInput`, `label`

#### `SliderRange`
Props: `valueFrom`, `valueTo`, `min`, `max`, `onChangeFrom`, `onChangeTo`, `showInput`

#### `SliderPercentage`
Props: `value`, `onChange`, `step`, `showInput`

---

### Booking

#### `BookingCell`
Props: `value`, `category` (`"blue"` `"red"` `"purple"` `"empty"`), `readOnly`, `deadline`, `onChange`

#### `BookingSlideshow`
Props: `tab` (`"details"` `"notes"` `"history"`), `onTabChange`, `rules` (`{ startDate, endDate, value? }[]`), `showVisible`, `showPhase`, `phase`, `showDateCreated`, `dateCreated`, `category`, `title`, `description`, `notes`, `history`, `hidden`, `notesCount`, `width`

---

### Side Panels

#### `SidePanel` (base)
Props: `open`, `onClose`, `children`, `width` (default 600)

#### `BookingSidePanel`
Props: `open`, `onClose`, `tab` (`"details"` `"notes"` `"history"` `"edit"` `"create-demand"` `"create-single"` `"create-repeated"` `"edit-repeated"` `"edit-hidden"` `"edit-not-editable"`), `data`

`data` fields: `wmName` `wmInitials` `roleName` `engagementName` `duration` `totalHours` `bookingCategory` `description` `title` `totalRules` `notes` `history` `onEdit` `onClone` `onReassign` `onRemove` `onSave`

Also available (all 400px wide): `ProfileSidePanel`, `EngagementSidePanel`, `RoleSidePanel`, `BookingCategorySidePanel`

---

### Feedback

#### `Alert`
Props: `type` (`"error"` `"warning"` `"success"` `"general"` `"ai"` `"bulk-banner"`), `layout` (`"inline"` `"with-header"`), `message`, `body`, `actions` (`{ label, onClick }[]` max 2)

#### `Tooltip`
Props: `content`, `children` (trigger), `placement` (`"down-center"` `"down-left"` `"down-right"` `"up-center"` `"up-left"` `"up-right"` `"left-center"` `"right-center"` `"no-arrow"`), `maxWidth`, `disabled`

#### `Toast` / `ToastProvider` / `useToast()`
Wrap app: `<ToastProvider>`. Use: `const { showToast } = useToast(); showToast({ type: "success", message: "Saved!" })`
`type`: `"success"` `"warning"` `"error"`

#### `EmptyState`
Props: `size` (`"big"` `"small-vertical"` `"small-horizontal"`), `title`, `subtitle`, `illustration`, `actions` (`{ label, kind, onClick }[]`), `showIcon`

#### `ProgressLinear`
Props: `value` (0–100), `showLabel`, `semantic`

#### `ProgressRadial`
Props: `value` (0–100), `showLabel`, `semantic`, `size` (px)

---

## SECTION 4 — TOKENS

**Use only these. Do not hardcode any hex colour or pixel size not in this list.**

### Colours

| Token | Hex | Use |
|---|---|---|
| `--palette-primary-0` | `#2358F8` | Primary blue — buttons, links, active |
| `--palette-primary-1` | `#1531B8` | Primary hover |
| `--palette-primary-2` | `#4B75FF` | Primary light |
| `--palette-primary-3` | `#E7F9FE` | Row selected bg |
| `--palette-primary-5` | `#436FB6` | Active badge bg |
| `--palette-primary-action` | `#6EF29C` | Shortlisting green |
| `--palette-blue-0` | `#0D2976` | Body text, headings |
| `--palette-blue-1` | `#0C1457` | Navbar, dark backgrounds |
| `--palette-blue-2` | `#5C6E9E` | Secondary text, muted icons |
| `--palette-blue-3` | `#31A2CE` | Accent |
| `--palette-neutral-0` | `#CFDAF7` | Borders, dividers |
| `--palette-neutral-1` | `#E7EAF8` | Selected bg, inactive badges |
| `--palette-neutral-2` | `#F8F9FD` | Page background |
| `--palette-neutral-3` | `#8F9ED1` | Disabled text |
| `--palette-white-0` | `#FFFFFF` | Card backgrounds |
| `--palette-white-1` | `#F7F7F8` | |
| `--palette-white-2` | `#ECECEC` | |
| `--palette-white-3` | `#D5D5D5` | |
| `--palette-black-0` | `#000000` | |
| `--palette-black-1` | `#333333` | |
| `--palette-red-0` | `#D42A36` | Error, destructive |
| `--palette-red-1` | `#A30013` | Error dark |
| `--palette-red-2` | `#FFE2E2` | Error background |
| `--palette-red-3` | `#FF0000` | |
| `--palette-green-0` | `#248E61` | Success, approved |
| `--palette-green-1` | `#1F6648` | Success dark |
| `--palette-green-2` | `#C8EEDE` | Success background |
| `--palette-orange-0` | `#FFCD38` | Warning |
| `--palette-orange-1` | `#9B5A01` | Warning text |
| `--palette-orange-2` | `#FFE8AD` | Warning background |
| `--palette-orange-3` | `#FF6B00` | |
| `--palette-orange-4` | `#FFE606` | |
| `--palette-reserved-0` | `#1F363D` | |
| `--palette-reserved-1` | `#5E7A83` | |
| `--palette-reserved-2` | `#40798C` | |
| `--palette-reserved-3` | `#70A9A1` | |
| `--palette-echarts-0` | `#5470C6` | Charts |
| `--palette-echarts-1` | `#91CC75` | Charts |
| `--palette-echarts-2` | `#FAC858` | Charts |
| `--palette-echarts-3` | `#EE6666` | Charts |
| `--palette-echarts-4` | `#73C0DE` | Charts |
| `--palette-echarts-5` | `#3BA272` | Charts |
| `--palette-echarts-6` | `#FC8452` | Charts |
| `--palette-echarts-7` | `#9A60B4` | Charts |
| `--palette-trans-0` | `rgba(0,0,0,0.04)` | Hover bg |
| `--palette-trans-1` | `rgba(0,0,0,0.08)` | |
| `--palette-trans-2` | `rgba(0,0,0,0.12)` | |
| `--palette-trans-light-0` | `rgba(255,255,255,0.04)` | |

### Typography

Font: **Mulish** always — never system fonts. Load via Google Fonts in `index.html`.

| Token | Value |
|---|---|
| `--font-family` | `"Mulish", sans-serif` |
| `--font-size-label-small` | 10px |
| `--font-size-label` | 12px |
| `--font-size-body` | 14px |
| `--font-size-h6` | 15px |
| `--font-size-h5` | 16px |
| `--font-size-h4` | 20px |
| `--font-size-h3` | 24px |
| `--font-size-h2` | 28px |
| `--font-size-h1` | 32px |
| `--font-weight-regular` | 400 |
| `--font-weight-semibold` | 600 |
| `--font-weight-bold` | 700 |
| `--line-height-small` | 115% |
| `--line-height-medium` | 125% |
| `--line-height-big` | 150% |

Named text styles:

| Name | Size | Weight | LH | Use |
|---|---|---|---|---|
| label-small-regular | 10px | 400 | 115% | Chart labels |
| label-small-bold | 10px | 700 | 115% | Breadcrumbs |
| label-regular | 12px | 400 | 150% | Secondary text, input labels |
| label-bold | 12px | 700 | 150% | Secondary text emphasized |
| label-selected | 12px | 700 | 115% | Small button labels |
| label-unselected | 12px | 400 | 115% | Small button labels (inactive) |
| body-regular | 14px | 400 | 150% | Body text, unselected tabs |
| body-bold | 14px | 700 | 150% | Body text emphasized |
| body-selected | 14px | 700 | 115% | Button labels, selected tabs |
| body-unselected | 14px | 400 | 115% | Button labels (inactive) |
| heading-6 | 15px | 600 | 125% | Tertiary titles |
| heading-5 | 16px | 600 | 125% | Section titles |
| heading-4 | 20px | 600 | 125% | Secondary titles |
| heading-3 | 24px | 600 | 125% | Section content titles |
| heading-2 | 28px | 600 | 125% | Page section titles |
| heading-1 | 32px | 600 | 125% | Page titles |

**Inline style shorthand (copy this exactly into every screen file):**
```tsx
const bodyBold: React.CSSProperties = { fontFamily: "var(--font-family)", fontSize: 14, fontWeight: 700, color: "var(--palette-blue-0)", lineHeight: "115%" };
const body:     React.CSSProperties = { fontFamily: "var(--font-family)", fontSize: 14, fontWeight: 400, color: "var(--palette-blue-0)", lineHeight: "150%" };
const label:    React.CSSProperties = { fontFamily: "var(--font-family)", fontSize: 12, fontWeight: 400, color: "var(--palette-blue-2)", lineHeight: "150%" };
const link:     React.CSSProperties = { fontFamily: "var(--font-family)", fontSize: 12, fontWeight: 400, color: "var(--palette-primary-0)", textDecoration: "none" };
```

### Spacing

| Token | Value |
|---|---|
| `--spacing-xs` | 2px |
| `--spacing-sm` | 4px |
| `--spacing-md` | 8px |
| `--spacing-md2` | 12px |
| `--spacing-lg` | 16px |
| `--spacing-xl` | 24px |
| `--spacing-2xl` | 32px |
| `--spacing-3xl` | 40px |

### Radii

| Token | Value |
|---|---|
| `--radius-xs` | 2px |
| `--radius-sm` | 4px |
| `--radius-md` | 8px |
| `--radius-lg` | 12px |
| `--radius-xl` | 16px |
| `--radius-2xl` | 32px |
| `--radius-full` | 9999px |

### Shadows

| Token | Value |
|---|---|
| `--tile-shadow-card` | `0px 0px 8px 0px rgba(203,225,242,0.8)` |
| `--tile-shadow-interactive` | `0px 4px 8px 0px rgba(203,225,242,0.8)` |

---

## SECTION 5 — SCAFFOLD

Run this when the prototype folder is empty.

**`package.json`**
```json
{
  "name": "profinda-prototype",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@ips/design-system": "file:PATH_TO_IPS_DESIGN_SYSTEM"
  },
  "notes": "Replace PATH_TO_IPS_DESIGN_SYSTEM with the local path to your clone of https://github.com/pedrorodrigopro/IPS-DesignSystem",
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "vite-plugin-singlefile": "^2.0.0",
    "typescript": "^5.0.0",
    "vite": "^6.0.0"
  }
}
```

> Ask the user for their local path to the IPS Design System repo and replace `PATH_TO_IPS_DESIGN_SYSTEM`.

**`vite.config.ts`**
```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
export default defineConfig({ plugins: [react(), viteSingleFile()] });
```

**`tsconfig.json`**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

**`index.html`**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ProFinda Prototype</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Mulish:wght@300;400;600;700;800&display=swap" rel="stylesheet" />
  </head>
  <body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>
```

**`src/main.tsx`** — import order is non-negotiable:
```tsx
import "@ips/design-system/styles/components";
import "./index.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
```

**`src/index.css`**
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Mulish', sans-serif;
  font-size: 14px;
  color: var(--palette-blue-0);
  background-color: var(--palette-neutral-2);
  -webkit-font-smoothing: antialiased;
}
```

After scaffolding: `npm install && npm run dev`

Tell the user: **"Your prototype is running at http://localhost:5173"**

### Page shell pattern (every screen uses this)
```tsx
<div style={{ height: "100vh", display: "flex", overflow: "hidden" }}>
  <Page navbar={<Navbar activeId="workflow" />} variant="1280">
    <div style={{ display: "flex", flexDirection: "column", gap: 16, width: "100%", paddingBottom: 32 }}>
      {/* screen content */}
    </div>
  </Page>
</div>
```

---

## SECTION 6 — ICONS

**Only these names are valid for `<Icon name="..." size={16} />`. Do not invent icon names.**

Size values: `14 | 16 | 20 | 24`

```
activity-feed  add  add-profile  admin  ai  ai-agent
arrow-2-directions  arrow-2-directions-vertical  arrow-4-directions
arrow-down  arrow-left  arrow-right  arrow-up
audit-planner  availability
baby  bag  bell  book  booking  bubbles  bug  bulk  bulk-move
calendar  calendar-clash  calendar-delete  calendar-misaligned
car  caret-down  caret-left  caret-right  caret-up
certificate  chat  check  chevron-down  chevron-left  chevron-right  chevron-up
clock  close-role  collapse  compare  copy  core  cost  created  cross
department  development  dot  dot-big  down  duplicate
edit  engagement  engagement-audit  error
expand  expand-all  expanded-all  export  extend
face-smile  facebook  filter  filter-applied  filter-clean  filter2
fire  flower-spa  folder  forbidden
ghost  head-heart  heart  heatmap  help  hidden  hierarchical  history  home
hourglass-empty  hourglass-half  house-laptop  house-user
import  industry  info  insights  instagram
key  keyboard
learning  link  linkedin  links  list  location  locked  logout
mail  manage-roles  mandatory  marketplace
menu-horizontal  menu-vertical  merge  missing  mobile  money  mouse-cursor  move
non-demand  note  notifications
open  overbooking  overbooking-acknowledged  owner
palm-tree  paper-clip  paper-plane  path  pen  person-minus  pf-logo
phone  pin  placeholder-profile  plane  play  postpone  preferences
profile  profile-field  profiles
question
reassign  refresh  refresh-clean  refresh-warning  remove  remove-all
reports  role  role-audit  rollforward
save  save-add  save-remove  search  sector  segment  share  shown
skills-framework  skype  skype-for-business  smart-allocation  snooze
soft-exception  sort  split  split2
substitute-child  substitute-parent  substitute-parent-child  subtract  suggested
table  tag  target-allocation  task  teams  timeline  twitter
undo  unpin  unseen  up  user-filled  user-interest
verified  verified-credly  verified-others
warning  web  wine-glass  work  workflow  zoom-in  zoom-out
```

---

## SECTION 7 — CHECKLIST

Run after every component placed. Fix anything that fails before moving on.

- [ ] `@ips/design-system/styles/components` is the **first** import in `main.tsx`
- [ ] No `style={{ padding }}` on any `Tile` — use `padding` prop
- [ ] No `style={{ background }}` on any `Tile` — use `tileStyle` prop
- [ ] No raw `<button>` anywhere — use `Button` from `@ips/design-system`
- [ ] No raw `<input>` as primary field — use IPS input components
- [ ] No raw `<div>` as a visible content box — use `Tile`
- [ ] Icon buttons in toolbars → `kind="icon"` (with border)
- [ ] Icon buttons inside cards → `kind="iconTertiary"` (no border)
- [ ] Text/link buttons ("Show more", "Add Reviewer") → `kind="link"`
- [ ] Only colour tokens from Section 4 used — no hardcoded hex
- [ ] Only icon names from Section 6 used — no invented names
- [ ] Font is Mulish — `index.html` has the Google Fonts `<link>` tags
- [ ] Build produces a single file → `vite-plugin-singlefile` in `vite.config.ts`

---

## SECTION 8 — DELIVER

```bash
npm run build
```

Output: `dist/index.html` — one portable file, all assets inlined.

Tell the user:
> "Your prototype is in `dist/index.html` — send it as an attachment or open it in any browser."
