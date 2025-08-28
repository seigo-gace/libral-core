# Libral Core Library Module

The Library Module serves as the shared "toolbox" for all Libral Core applications and modules. It provides common functionality that eliminates code duplication and ensures consistent operations across the entire platform.

## Architecture Overview

The Library Module is designed as an independent layer that sits between the Libral Core and individual apps, providing three main categories of functionality:

```
┌─────────────────────────────────────────────┐
│                Apps Layer                   │
│  (TxT WORLD Creator's, LIVE VIDEO CHAT,    │
│   Libral AI, etc.)                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Library Module                   │
│  ┌─────────────┬─────────────┬─────────────┐│
│  │    utils    │ api_clients │file_handlers││
│  └─────────────┴─────────────┴─────────────┘│
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              Libral Core                    │
│    (GPG, Auth, Events, Payments, etc.)     │
└─────────────────────────────────────────────┘
```

## Modules

### 1. Utils Submodule

Provides common utility functions for string processing, datetime handling, and data validation.

#### StringUtils
- `sanitize_text(text: str) -> str`: Remove dangerous characters from user input
- `truncate_text(text: str, length: int) -> str`: Truncate text for UI display
- `extract_hashtags(text: str) -> List[str]`: Extract hashtags for Telegram topics
- `validate_telegram_username(username: str) -> bool`: Validate Telegram usernames

#### DateTimeUtils
- `format_datetime_utc(dt: datetime) -> str`: Convert to ISO 8601 UTC format
- `parse_datetime_utc(dt_string: str) -> datetime`: Parse UTC datetime strings
- `format_relative_time(dt: datetime) -> str`: Format as "2 hours ago"
- `format_timestamp_for_telegram(dt: datetime) -> str`: Telegram-compatible timestamps

### 2. API Clients Submodule

Unified clients for external API communication with consistent authentication and error handling.

#### BaseAPIClient
- Foundation class with retry logic, authentication, and error handling
- Automatic request/response logging and performance monitoring
- Configurable timeouts and retry strategies

#### ExternalSearchClient
- Search external APIs for real-time information
- Support for multiple providers (Google, Bing, DuckDuckGo)
- Structured result formatting for AI consumption

### 3. File Handlers Submodule

Media file processing capabilities for images and videos.

#### ImageProcessor
- `create_sticker(text, font_path, bg_path) -> bytes`: Core TxT WORLD Creator's function
- `resize_image(image_bytes, max_size) -> bytes`: Performance optimization
- `add_watermark(image_bytes, text) -> bytes`: Content protection
- `convert_format(image_bytes, format) -> bytes`: Format conversion

#### VideoProcessor
- `convert_to_gif(video_bytes) -> bytes`: Video to GIF for LIVE VIDEO CHAT
- `compress_video(video_bytes) -> bytes`: Bandwidth optimization
- `extract_thumbnail(video_bytes) -> bytes`: Video preview generation

## Usage Examples

### Basic String Processing
```python
from libral_core.library import StringUtils

# Sanitize user input
safe_text = StringUtils.sanitize_text("<script>alert('xss')</script>Hello")
# Result: "Hello"

# Truncate for UI display
short_text = StringUtils.truncate_text("Very long text here", 10)
# Result: "Very lo..."
```

### External API Integration
```python
from libral_core.library import ExternalSearchClient

# Initialize search client
client = ExternalSearchClient("your_api_key", "google")

# Search for real-time information
results = client.search("Libral Core features")
for result in results:
    print(f"{result['title']}: {result['url']}")
```

### Image Processing
```python
from libral_core.library import ImageProcessor

# Create sticker for TxT WORLD Creator's
processor = ImageProcessor()
sticker_data = processor.create_sticker(
    text="Hello World!",
    font_path="/fonts/comic.ttf",
    bg_path="/backgrounds/space.jpg"
)

# Save the sticker
with open("sticker.png", "wb") as f:
    f.write(sticker_data)
```

### Video Processing
```python
from libral_core.library import VideoProcessor

# Convert video to GIF for sharing
processor = VideoProcessor()
with open("video.mp4", "rb") as f:
    video_data = f.read()

gif_data = processor.convert_to_gif(video_data, max_duration=5)
with open("animation.gif", "wb") as f:
    f.write(gif_data)
```

## Design Principles

### 1. Code Reuse and DRY
The Library Module eliminates code duplication by centralizing common functionality. Instead of each app implementing its own string sanitization or image processing, they all use the same tested and optimized implementations.

### 2. Consistent Interfaces
All utilities provide consistent APIs and error handling patterns. This makes the codebase more maintainable and reduces the learning curve for developers.

### 3. Security First
Security considerations are built into every utility, from input sanitization to secure API communication. This ensures that security best practices are followed across all apps.

### 4. Performance Optimization
Common operations are optimized once in the Library Module and benefit all apps. This includes image processing optimizations, efficient datetime handling, and smart caching strategies.

### 5. Platform Compatibility
The Library Module handles platform-specific considerations (like Telegram's requirements) in one place, ensuring all apps work correctly across different environments.

## Dependencies

### Required Python Packages
- `Pillow`: Image processing capabilities
- `requests`: HTTP client functionality  
- `iso8601`: ISO 8601 datetime parsing
- `subprocess`: Video processing (requires FFmpeg)

### System Dependencies
- **FFmpeg**: Required for video processing features
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ffmpeg
  
  # macOS with Homebrew
  brew install ffmpeg
  ```

## Testing

Run the test suite to ensure all functionality works correctly:

```bash
cd libral-core
python -m pytest libral_core/library/tests/ -v
```

## Development Guidelines

### Adding New Utilities
1. Place utility functions in appropriate submodules (utils, api_clients, file_handlers)
2. Follow existing naming conventions and documentation patterns
3. Include comprehensive error handling and logging
4. Add unit tests for all new functionality
5. Update this README with usage examples

### Security Considerations
- Always validate and sanitize user input
- Use secure defaults for all configurations
- Implement proper error handling without exposing sensitive information
- Follow the principle of least privilege for API access

### Performance Guidelines
- Optimize for common use cases
- Implement caching where appropriate
- Use efficient algorithms and data structures
- Monitor memory usage for file processing operations

## Integration with Libral Core

The Library Module integrates seamlessly with Libral Core through its modular architecture:

1. **Loose Coupling**: Apps use the Library Module without depending on Libral Core internals
2. **Event Integration**: Utilities can emit events that Libral Core processes
3. **Configuration**: Library settings are managed through Libral Core configuration system
4. **Monitoring**: All Library operations are monitored through Libral Core's metrics system

This design enables rapid development of new apps while maintaining the stability and security of the core platform.