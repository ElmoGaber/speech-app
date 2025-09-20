"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Mic, MicOff, Volume2, Copy, Trash2, Square } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message: string
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  addEventListener(type: "result", listener: (event: SpeechRecognitionEvent) => void): void
  addEventListener(type: "error", listener: (event: SpeechRecognitionErrorEvent) => void): void
  addEventListener(type: "start", listener: () => void): void
  addEventListener(type: "end", listener: () => void): void
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
}

export default function SpeechRecognitionComponent() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [interimTranscript, setInterimTranscript] = useState("")
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [textToSpeak, setTextToSpeak] = useState("")
  const [isSupported, setIsSupported] = useState(true)
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    // Check if speech recognition is supported
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!SpeechRecognition) {
        setIsSupported(false)
        return
      }

      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = "en-US"

      recognition.addEventListener("result", (event: SpeechRecognitionEvent) => {
        let finalTranscript = ""
        let interimTranscript = ""

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }

        setTranscript((prev) => prev + finalTranscript)
        setInterimTranscript(interimTranscript)
      })

      recognition.addEventListener("start", () => {
        setIsListening(true)
        console.log("[v0] Speech recognition started")
      })

      recognition.addEventListener("end", () => {
        setIsListening(false)
        setInterimTranscript("")
        console.log("[v0] Speech recognition ended")
      })

      recognition.addEventListener("error", (event: SpeechRecognitionErrorEvent) => {
        console.log("[v0] Speech recognition error:", event.error)
        setIsListening(false)
        toast({
          title: "Speech Recognition Error",
          description: `Error: ${event.error}. Please try again.`,
          variant: "destructive",
        })
      })

      recognitionRef.current = recognition
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [toast])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start()
        toast({
          title: "Listening Started",
          description: "Speak now, I'm listening...",
        })
      } catch (error) {
        console.log("[v0] Error starting recognition:", error)
        toast({
          title: "Error",
          description: "Failed to start speech recognition",
          variant: "destructive",
        })
      }
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
      toast({
        title: "Listening Stopped",
        description: "Speech recognition has been stopped.",
      })
    }
  }

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      // Stop any ongoing speech
      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.8
      utterance.pitch = 1
      utterance.volume = 1

      utterance.onstart = () => {
        setIsSpeaking(true)
        console.log("[v0] Text-to-speech started")
      }

      utterance.onend = () => {
        setIsSpeaking(false)
        console.log("[v0] Text-to-speech ended")
      }

      utterance.onerror = (event) => {
        setIsSpeaking(false)
        console.log("[v0] Text-to-speech error:", event.error)
        toast({
          title: "Speech Synthesis Error",
          description: "Failed to speak the text. Please try again.",
          variant: "destructive",
        })
      }

      window.speechSynthesis.speak(utterance)
      toast({
        title: "Speaking",
        description: "Converting text to speech...",
      })
    } else {
      toast({
        title: "Not Supported",
        description: "Text-to-speech is not supported in your browser.",
        variant: "destructive",
      })
    }
  }

  const stopSpeaking = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      toast({
        title: "Speech Stopped",
        description: "Text-to-speech has been stopped.",
      })
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast({
        title: "Copied!",
        description: "Text has been copied to clipboard.",
      })
    } catch (error) {
      console.log("[v0] Copy error:", error)
      toast({
        title: "Copy Failed",
        description: "Failed to copy text to clipboard.",
        variant: "destructive",
      })
    }
  }

  const clearTranscript = () => {
    setTranscript("")
    setInterimTranscript("")
    toast({
      title: "Cleared",
      description: "Transcript has been cleared.",
    })
  }

  if (!isSupported) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="font-space-grotesk text-destructive">Not Supported</CardTitle>
            <CardDescription>
              Speech recognition is not supported in your browser. Please use a modern browser like Chrome, Edge, or
              Safari.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold font-space-grotesk text-foreground">Speech Recognition & Text-to-Speech</h1>
          <p className="text-muted-foreground font-dm-sans">
            AI-powered speech recognition and text-to-speech conversion for enhanced accessibility and automation
          </p>
        </div>

        {/* Speech Recognition Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-space-grotesk flex items-center gap-2">
                  <Mic className="h-5 w-5" />
                  Speech Recognition
                </CardTitle>
                <CardDescription className="font-dm-sans">
                  Click the microphone to start converting speech to text
                </CardDescription>
              </div>
              <Badge variant={isListening ? "default" : "secondary"} className="font-dm-sans">
                {isListening ? "Listening..." : "Ready"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Button
                onClick={isListening ? stopListening : startListening}
                variant={isListening ? "destructive" : "default"}
                size="lg"
                className="font-dm-sans"
              >
                {isListening ? (
                  <>
                    <MicOff className="h-4 w-4 mr-2" />
                    Stop Listening
                  </>
                ) : (
                  <>
                    <Mic className="h-4 w-4 mr-2" />
                    Start Listening
                  </>
                )}
              </Button>
              {transcript && (
                <>
                  <Button
                    onClick={() => copyToClipboard(transcript)}
                    variant="outline"
                    size="lg"
                    className="font-dm-sans"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button onClick={clearTranscript} variant="outline" size="lg" className="font-dm-sans bg-transparent">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear
                  </Button>
                </>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium font-dm-sans">Recognized Text:</label>
              <Textarea
                value={transcript + interimTranscript}
                readOnly
                placeholder="Your speech will appear here..."
                className="min-h-32 font-dm-sans"
              />
              {interimTranscript && (
                <p className="text-xs text-muted-foreground font-dm-sans">
                  <span className="text-accent">Interim:</span> {interimTranscript}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Text-to-Speech Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-space-grotesk flex items-center gap-2">
                  <Volume2 className="h-5 w-5" />
                  Text-to-Speech
                </CardTitle>
                <CardDescription className="font-dm-sans">Enter text to convert to speech</CardDescription>
              </div>
              <Badge variant={isSpeaking ? "default" : "secondary"} className="font-dm-sans">
                {isSpeaking ? "Speaking..." : "Ready"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium font-dm-sans">Text to Speak:</label>
              <Textarea
                value={textToSpeak}
                onChange={(e) => setTextToSpeak(e.target.value)}
                placeholder="Enter text to convert to speech..."
                className="min-h-32 font-dm-sans"
              />
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => speakText(textToSpeak)}
                disabled={!textToSpeak.trim() || isSpeaking}
                size="lg"
                variant="secondary"
                className="font-dm-sans"
              >
                <Volume2 className="h-4 w-4 mr-2" />
                Speak Text
              </Button>
              {transcript && (
                <Button
                  onClick={() => speakText(transcript)}
                  disabled={!transcript.trim() || isSpeaking}
                  size="lg"
                  variant="outline"
                  className="font-dm-sans"
                >
                  <Volume2 className="h-4 w-4 mr-2" />
                  Speak Recognition
                </Button>
              )}
              {isSpeaking && (
                <Button onClick={stopSpeaking} variant="destructive" size="lg" className="font-dm-sans">
                  <Square className="h-4 w-4 mr-2" />
                  Stop Speaking
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card className="bg-muted/50">
          <CardHeader>
            <CardTitle className="font-space-grotesk text-lg">How to Use</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 font-dm-sans text-sm">
            <div>
              <h4 className="font-medium mb-1">Speech Recognition:</h4>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Click "Start Listening" and speak clearly into your microphone</li>
                <li>Your speech will be converted to text in real-time</li>
                <li>Click "Stop Listening" when you're done speaking</li>
                <li>Use "Copy" to copy the text or "Clear" to start over</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-1">Text-to-Speech:</h4>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Type or paste text in the text area</li>
                <li>Click "Speak Text" to hear the text read aloud</li>
                <li>Use "Speak Recognition" to hear your recognized speech</li>
                <li>Click "Stop Speaking" to interrupt the speech</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
