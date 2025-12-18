import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

const Button = ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => (
    <button onClick={onClick}>{children}</button>
)

describe('Button', () => {
    it('renders children correctly', () => {
        render(<Button>Click me</Button>)
        expect(screen.getByText('Click me')).toBeInTheDocument()
    })
})
