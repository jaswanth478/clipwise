# ClipWise Frontend

A beautiful, modern Next.js frontend for the ClipWise AI-powered video clipping platform.

## Features

- 🎨 **Modern UI/UX** - Beautiful, responsive design with smooth animations
- 📱 **Mobile-First** - Optimized for all devices
- ⚡ **Fast & Smooth** - Built with Next.js 14 and Framer Motion
- 🎯 **User-Friendly** - Simple URL input with copy-paste functionality
- 🎬 **Video Preview** - Interactive clip cards with video previews
- 📊 **Rich Metadata** - Display interest scores, reasons, and file info
- 🚀 **V2 Preview** - Showcase upcoming features

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## API Integration

The frontend connects to your ClipWise API at `http://localhost:5001/clip`. Make sure your backend is running and accessible.

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Lucide React** - Icons

## Project Structure

```
FrontEnd/
├── app/
│   ├── components/
│   │   ├── ClipCard.tsx      # Individual clip display
│   │   ├── UrlInput.tsx      # URL input form
│   │   └── V2Features.tsx    # V2 features preview
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Main page
├── package.json
├── tailwind.config.js
└── README.md
```

## Features in Detail

### URL Input
- YouTube URL validation
- Copy-paste functionality
- Loading states
- Error handling

### Clip Display
- Video preview with play button
- Interest score and reasons
- Download and share functionality
- Like/unlike clips
- Copy URL functionality

### V2 Features Preview
- Team collaboration
- Custom branding
- Background music
- Mobile app
- Multi-platform support
- Analytics dashboard
- Cloud storage
- Advanced security

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Styling

The project uses Tailwind CSS with custom animations and components. Key custom classes:

- `.gradient-bg` - Gradient backgrounds
- `.glass-effect` - Glass morphism effects
- `.clip-card` - Clip card hover animations
- `.loading-dots` - Loading animation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the ClipWise platform. 