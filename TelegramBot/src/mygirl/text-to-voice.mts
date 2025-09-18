import axios from 'axios'
import _ from 'lodash'
import dotenv from 'dotenv'

dotenv.config()

export const textToVoice = async (
  textContent: string,
  options?: { voice_preset?: string; text_temp?: number; waveform_temp?: number },
): Promise<string> => {
  console.log('call textToVoice', textContent)
  return new Promise((resolve, reject) => {
    const start = Date.now()
    axios
      .post(
        // @ts-ignore
        process.env.TTS_SERVER,
        {
          text: textContent,
          voice_preset: options?.voice_preset,
          text_temp: options?.text_temp,
          waveform_temp: options?.waveform_temp,
        },
        {
          onDownloadProgress: (e) => {
            console.log('onDownloadProgress', Date.now(), e.loaded)
          },
        },
      )
      .then((result) => {
        console.log('call textToVoice success', Date.now(), result.data?.file_base64?.length, Date.now() - start)
        const data = result.data?.file_base64
        if (_.isEmpty(data)) {
          reject(new Error('no data'))
          return
        }
        resolve(data)
      })
      .catch((e) => {
        console.log('call textToVoice failed', e)
        reject(e)
      })
  })
}
