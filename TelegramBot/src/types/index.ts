export interface ExchangeMessageData {
  user: {
    id: string
  }
  chat: {
    id: string
  }
  message: {
    type: 'text' | 'image' | 'voice' | 'command'
    content: string
    id: string
  }
  options?: {
    voice: boolean
    voice_preset?: string
    text_temp?: number
    waveform_temp?: number
    voice_call?: boolean
  }
}

export interface GPTResponseData {
  content: string
  imageBase64: string
}
