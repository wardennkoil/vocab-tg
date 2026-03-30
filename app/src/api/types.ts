// TypeScript interfaces mirroring api/app/schemas/*.py

// --- Users ---

export interface UserRegister {
  telegram_id: number
  username?: string | null
  first_name?: string | null
  language_code?: string | null
}

export interface UserSettingsUpdate {
  timezone?: string | null
  daily_push_hour?: number | null
  daily_word_count?: number | null
  difficulty_level?: string | null
  skip_triage?: boolean | null
}

export interface UserResponse {
  id: number
  telegram_id: number
  username: string | null
  first_name: string | null
  timezone: string
  daily_push_hour: number
  daily_word_count: number
  difficulty_level: string
  skip_triage: boolean
  is_active: boolean
  created_at: string
}

// --- Words ---

export interface WordCard {
  id: number
  word: string
  phonetic: string | null
  audio_url: string | null
  definition: string | null
  definitions_json: Record<string, unknown>[] | null
  translation_ru: string | null
  example_sentence: string | null
  synonyms: string[]
  antonyms: string[]
  part_of_speech: string | null
  difficulty_band: string | null
}

export interface WordSuggestion {
  word: string
  score: number
}

export interface UserWordResponse {
  id: number
  user_id: number
  word_id: number
  status: string
  source: string
  due_at: string | null
  reps: number
  lapses: number
  added_at: string
  last_reviewed_at: string | null
  word: WordCard
}

export interface PaginatedUserWords {
  items: UserWordResponse[]
  total: number
  page: number
  per_page: number
}

// --- Daily ---

export interface TriageCandidate {
  word_id: number
  word: string
  definition: string | null
}

export interface TriageCandidatesResponse {
  candidates: TriageCandidate[]
  session_id: number
}

export interface TriageSubmitPayload {
  session_id: number
  known_word_ids: number[]
  unknown_word_ids: number[]
}

export interface DailyWordsResponse {
  words: WordCard[]
  session_date: string
  status: string
}

// --- Reviews ---

export type ReviewType =
  | 'multiple_choice'
  | 'reverse_mcq'
  | 'fill_blank_mcq'
  | 'fill_blank_type'
  | 'matching'
  | 'odd_one_out'
  | 'true_false'
  | 'word_in_context'

export interface MCQData {
  options: WordCard[]
  correct_index: number
}

export interface ReverseMCQData {
  definition_options: string[]
  correct_index: number
}

export interface FillBlankMCQData {
  sentence_with_blank: string
  options: string[]
  correct_index: number
}

export interface FillBlankTypeData {
  sentence_with_blank: string
  correct_answer: string
  accept_alternatives: string[]
}

export interface MatchingPair {
  user_word_id: number
  word: string
  definition: string
}

export interface MatchingData {
  pairs: MatchingPair[]
}

export interface OddOneOutData {
  words: string[]
  odd_index: number
}

export interface TrueFalseData {
  shown_definition: string
  is_correct_pair: boolean
}

export interface WordInContextData {
  sentence: string
  definition_options: string[]
  correct_index: number
}

export interface ReviewItem {
  type: ReviewType
  user_word_id: number | null
  word: WordCard | null
  mcq_data: MCQData | null
  reverse_mcq_data: ReverseMCQData | null
  fill_blank_mcq_data: FillBlankMCQData | null
  fill_blank_type_data: FillBlankTypeData | null
  matching_data: MatchingData | null
  odd_one_out_data: OddOneOutData | null
  true_false_data: TrueFalseData | null
  word_in_context_data: WordInContextData | null
}

export interface ReviewSession {
  items: ReviewItem[]
  total: number
  due_count: number
}

export interface ReviewSubmitPayload {
  user_word_id: number
  review_type: ReviewType
  was_correct: boolean
  response_time_ms?: number | null
  typed_answer?: string | null
}

export interface ReviewBatchSubmitPayload {
  review_type: 'matching'
  results: ReviewSubmitPayload[]
  total_time_ms?: number | null
}

export interface ReviewResult {
  user_word_id: number
  next_due: string | null
  was_correct: boolean | null
  rating: number
}

export interface ReviewBatchResult {
  results: ReviewResult[]
}

// --- Stats ---

export interface StatsOverview {
  total_words: number
  words_learning: number
  words_known: number
  current_streak: number
  accuracy_rate: number | null
  reviews_today: number
  due_tomorrow: number
}

export interface DayStats {
  date: string
  review_count: number
}

export interface StatsHistory {
  days: DayStats[]
}
