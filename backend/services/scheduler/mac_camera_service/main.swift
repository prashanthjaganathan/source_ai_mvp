// /backend/services/scheduler/mac_camera_service/main.swift
import Foundation
import AVFoundation
import AppKit

class MacCameraService: NSObject, AVCapturePhotoCaptureDelegate {
    private let captureSession = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()
    private var isSessionConfigured = false
    
    override init() {
        super.init()
        setupCaptureSession()
    }
    
    func setupCaptureSession() {
        // Configure session for photo capture
        captureSession.sessionPreset = .photo
        
        // Get the default video device (Mac's camera)
        guard let videoDevice = AVCaptureDevice.default(for: .video) else {
            print("No camera found")
            return
        }
        
        do {
            // Create input from the video device
            let videoInput = try AVCaptureDeviceInput(device: videoDevice)
            
            // Add input and output to session
            if captureSession.canAddInput(videoInput) {
                captureSession.addInput(videoInput)
            }
            
            if captureSession.canAddOutput(photoOutput) {
                captureSession.addOutput(photoOutput)
            }
            
            isSessionConfigured = true
            print("Camera session configured successfully")
            
        } catch {
            print("Error setting up camera: \(error)")
        }
    }
    
    func startSession() {
        guard isSessionConfigured else {
            print("Session not configured")
            return
        }
        
        if !captureSession.isRunning {
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                self?.captureSession.startRunning()
                print("Camera session started")
            }
        }
    }
    
    func stopSession() {
        if captureSession.isRunning {
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                self?.captureSession.stopRunning()
                print("Camera session stopped")
            }
        }
    }
    
    func capturePhoto(to path: String, completion: @escaping (Bool, String?) -> Void) {
        guard isSessionConfigured && captureSession.isRunning else {
            completion(false, "Camera session not ready")
            return
        }
        
        // Configure photo settings
        let photoSettings = AVCapturePhotoSettings()
        photoSettings.isHighResolutionPhotoEnabled = false
        
        // Set completion handler
        photoOutput.capturePhoto(with: photoSettings, delegate: PhotoCaptureDelegate(path: path, completion: completion))
    }
    
    // Helper class to handle photo capture completion
    private class PhotoCaptureDelegate: NSObject, AVCapturePhotoCaptureDelegate {
        private let outputPath: String
        private let completion: (Bool, String?) -> Void
        
        init(path: String, completion: @escaping (Bool, String?) -> Void) {
            self.outputPath = path
            self.completion = completion
        }
        
        func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
            if let error = error {
                completion(false, "Photo capture error: \(error.localizedDescription)")
                return
            }
            
            guard let imageData = photo.fileDataRepresentation() else {
                completion(false, "Could not get image data")
                return
            }
            
            do {
                // Create directory if it doesn't exist
                let directory = URL(fileURLWithPath: outputPath).deletingLastPathComponent()
                try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true, attributes: nil)
                
                // Save the photo
                try imageData.write(to: URL(fileURLWithPath: outputPath))
                completion(true, nil)
                
            } catch {
                completion(false, "Error saving photo: \(error.localizedDescription)")
            }
        }
    }
}

// Global camera service instance
let cameraService = MacCameraService()

// Signal handler for graceful shutdown
signal(SIGINT) { _ in
    cameraService.stopSession()
    exit(0)
}

// Main execution
func main() {
    print("Starting Mac Camera Service...")
    
    // Request camera permission
    AVCaptureDevice.requestAccess(for: .video) { granted in
        if granted {
            print("Camera permission granted")
            cameraService.startSession()
        } else {
            print("Camera permission denied")
            exit(1)
        }
    }
    
    // Keep the service running
    RunLoop.main.run()
}

main()