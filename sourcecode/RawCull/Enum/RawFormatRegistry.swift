//
//  RawFormatRegistry.swift
//  RawCull
//
//  Dispatches by file extension to the matching `RawFormat` conformer.
//  Add a new brand by appending its conformer to `all`.
//

import Foundation

enum RawFormatRegistry {
    nonisolated static let all: [any RawFormat.Type] = [
        SonyRawFormat.self,
        NikonRawFormat.self
    ]

    /// Union of extensions across every registered format.
    nonisolated static var allExtensions: Set<String> {
        all.reduce(into: Set<String>()) { $0.formUnion($1.extensions) }
    }

    /// Resolves the format for a file URL by its lowercased extension.
    nonisolated static func format(for url: URL) -> (any RawFormat.Type)? {
        let ext = url.pathExtension.lowercased()
        return all.first { $0.extensions.contains(ext) }
    }
}
