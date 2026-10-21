import Foundation
import Vision
import ImageIO
// One image per invocation; original PDF pages are rendered by the Python pipeline.
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true
let handler = VNImageRequestHandler(url: url, options: [:])
do {
 try handler.perform([request])
 let rows = (request.results ?? []).compactMap { result -> [String: Any]? in
  guard let text = result.topCandidates(1).first else { return nil }
  return ["text": text.string, "confidence": text.confidence, "box": [result.boundingBox.origin.x, result.boundingBox.origin.y, result.boundingBox.width, result.boundingBox.height]]
 }
 let data = try JSONSerialization.data(withJSONObject: rows, options: [.sortedKeys])
 print(String(data: data, encoding: .utf8)!)
} catch { fputs("OCR failed: \(error)\n", stderr); exit(1) }
