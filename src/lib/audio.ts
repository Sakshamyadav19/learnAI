// Audio utility functions for converting base64 audio to playable URLs

/**
 * Converts a base64-encoded audio string to a playable audio URL
 * @param audioBase64 - Base64 encoded audio data (WAV format)
 * @returns Object URL that can be used in HTML audio element
 */
export function convertBase64ToAudioUrl(audioBase64: string): string {
  if (!audioBase64 || audioBase64.trim() === "") {
    throw new Error("Empty or invalid base64 audio data");
  }

  try {
    // Decode base64 string to binary
    // Handle both with and without data URI prefix
    let base64Data = audioBase64;
    if (audioBase64.includes(",")) {
      base64Data = audioBase64.split(",")[1];
    }

    // Convert base64 to binary string
    const binaryString = atob(base64Data);
    
    // Convert binary string to Uint8Array
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Create Blob with audio MIME type
    // Try to detect format from header, default to audio/mpeg (MP3) or audio/wav
    let mimeType = "audio/mpeg"; // Default to MP3 as per test_audio.py pattern
    if (bytes.length >= 4) {
      // Check for WAV (RIFF header)
      if (bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46) {
        mimeType = "audio/wav";
      }
      // Check for MP3 (ID3 header or sync frame)
      else if (
        (bytes[0] === 0x49 && bytes[1] === 0x44 && bytes[2] === 0x33) ||
        (bytes[0] === 0xff && (bytes[1] & 0xe0) === 0xe0)
      ) {
        mimeType = "audio/mpeg";
      }
    }
    
    const blob = new Blob([bytes], { type: mimeType });

    // Create object URL from blob
    const audioUrl = URL.createObjectURL(blob);

    return audioUrl;
  } catch (error) {
    throw new Error(`Failed to convert base64 audio to URL: ${error}`);
  }
}

/**
 * Revokes an object URL to free up memory
 * Should be called when the audio is no longer needed
 * @param audioUrl - The object URL to revoke
 */
export function revokeAudioUrl(audioUrl: string): void {
  if (audioUrl && audioUrl.startsWith("blob:")) {
    URL.revokeObjectURL(audioUrl);
  }
}

