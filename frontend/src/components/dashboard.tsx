"use client"

import { useState } from "react"
import { Bell, Search, Settings, LayoutDashboard, User, Menu, X, Lock, Users, Monitor, RefreshCw, Trash2, Sun, Moon } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// Nova Logo Component
function NovaLogo({ size = "w-6 h-7", innerSize = "w-4.5 h-5.5", theme }: { size?: string; innerSize?: string; theme: "dark" | "light" }) {
  return (
    <div
      className={`${size} ${
        theme === "dark"
          ? "bg-gradient-to-b from-cyan-400 to-blue-500"
          : "bg-gradient-to-b from-cyan-500 to-blue-600"
      } flex items-center justify-center`}
      style={{
        clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
      }}
    >
      <div
        className={`${innerSize} ${
          theme === "dark" ? "bg-slate-950" : "bg-white"
        }`}
        style={{
          clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
        }}
      />
    </div>
  )
}

// Mock data for file locks
const mockFileLocks = [
  {
    id: 1,
    file: "Engine_Assembly.dwg",
    path: "C:\\Projects\\Engine_Assembly.dwg",
    user: "John Smith",
    pid: 2048,
    computer: "WORKSTATION-01",
    lockedSince: "1/15/2024, 6:30:00 AM",
  },
  {
    id: 2,
    file: "Chassis_Design.dwg",
    path: "D:\\CAD\\Chassis_Design.dwg",
    user: "Sarah Johnson",
    pid: 1024,
    computer: "WORKSTATION-03",
    lockedSince: "1/15/2024, 5:45:00 AM",
  },
  {
    id: 3,
    file: "Suspension_System.dwg",
    path: "E:\\Designs\\Suspension_System.dwg",
    user: "Mike Chen",
    pid: 3072,
    computer: "WORKSTATION-07",
    lockedSince: "1/15/2024, 4:15:00 AM",
  },
]

export default function Dashboard() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [activeTab, setActiveTab] = useState("dashboard")
  const [theme, setTheme] = useState("dark")
  const [searchQuery, setSearchQuery] = useState("")
  const [fileLocks, setFileLocks] = useState(mockFileLocks)
  const [notifications, setNotifications] = useState(3)

  // Filter file locks based on search query
  const filteredFileLocks = fileLocks.filter(
    (lock) =>
      lock.file.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lock.user.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lock.computer.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const handleRefresh = () => {
    // Simulate refresh
    console.log("[v0] Refreshing file locks...")
  }

  const handleCleanup = () => {
    // Simulate cleanup
    console.log("[v0] Cleaning up stale locks...")
  }

  const handleRemoveLock = (id: number) => {
    setFileLocks((prev) => prev.filter((lock) => lock.id !== id))
  }

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"))
  }

  const sidebarItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "profile", label: "Profile", icon: User },
    { id: "settings", label: "Settings", icon: Settings },
  ]

  return (
    <div
      className={`min-h-screen transition-colors duration-300 ${
        theme === "dark"
          ? "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"
          : "bg-gradient-to-br from-slate-50 via-white to-slate-100"
      }`}
    >
      {/* Animated background particles */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div
          className={`absolute inset-0 ${
            theme === "dark"
              ? "bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.1),transparent_50%)]"
              : "bg-[radial-gradient(circle_at_50%_50%,rgba(59,130,246,0.05),transparent_50%)]"
          }`}
        />
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className={`absolute w-1 h-1 rounded-full animate-pulse ${
              theme === "dark" ? "bg-cyan-400/20" : "bg-cyan-600/30"
            }`}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 flex h-screen">
        {/* Sidebar */}
        <div
          className={`${sidebarCollapsed ? "w-16" : "w-64"} transition-all duration-300 ${
            theme === "dark" ? "bg-slate-900/80 border-slate-700/50" : "bg-white/80 border-slate-200/50"
          } backdrop-blur-xl border-r flex flex-col`}
        >
          {/* Sidebar Header */}
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex items-center justify-between">
              {!sidebarCollapsed && (
                <div className="flex items-center space-x-3">
                  <NovaLogo theme={theme as "dark" | "light"} />
                  <span className={`font-bold text-lg ${theme === "dark" ? "text-white" : "text-slate-900"}`}>
                    Nova
                  </span>
                </div>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className={`${
                  theme === "dark"
                    ? "text-slate-400 hover:text-white hover:bg-slate-800"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                {sidebarCollapsed ? <Menu className="w-4 h-4" /> : <X className="w-4 h-4" />}
              </Button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4">
            <div className="space-y-2">
              {sidebarItems.map((item) => {
                const Icon = item.icon
                return (
                  <Button
                    key={item.id}
                    variant={activeTab === item.id ? "default" : "ghost"}
                    className={`w-full justify-start ${sidebarCollapsed ? "px-2" : "px-3"} ${
                      activeTab === item.id
                        ? theme === "dark"
                          ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white"
                          : "bg-gradient-to-r from-cyan-600 to-blue-600 text-white"
                        : theme === "dark"
                          ? "text-slate-400 hover:text-white hover:bg-slate-800"
                          : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                    }`}
                    onClick={() => setActiveTab(item.id)}
                  >
                    <Icon className="w-4 h-4" />
                    {!sidebarCollapsed && <span className="ml-3">{item.label}</span>}
                  </Button>
                )
              })}
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header
            className={`${
              theme === "dark" ? "bg-slate-900/80 border-slate-700/50" : "bg-white/80 border-slate-200/50"
            } backdrop-blur-xl border-b px-6 py-4`}
          >
            <div className="flex items-center justify-between">
              <div>
              <div className="flex items-center space-x-3">
                  <NovaLogo theme={theme as "dark" | "light"} />
                  <h1
                  className={`text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent`}
                >
                  Nova
                </h1>
                </div>
                
                <p className={`text-sm ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`}>
                  Manage file locks in real time
                </p>
              </div>

              <div className="flex items-center space-x-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleTheme}
                  className={`${
                    theme === "dark"
                      ? "text-slate-400 hover:text-white hover:bg-slate-800"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  className={`relative ${
                    theme === "dark"
                      ? "text-slate-400 hover:text-white hover:bg-slate-800"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  <Bell className="w-4 h-4" />
                  {notifications > 0 && (
                    <Badge className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center text-xs bg-red-500 text-white">
                      {notifications}
                    </Badge>
                  )}
                </Button>

                <div
                  className={`w-8 h-10 ${
                    theme === "dark"
                      ? "bg-gradient-to-b from-cyan-400 to-blue-500"
                      : "bg-gradient-to-b from-cyan-500 to-blue-600"
                  } flex items-center justify-center text-white font-semibold text-sm`}
                  style={{
                    clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
                  }}
                >
                  CM
                </div>
              </div>
            </div>
          </header>

          {/* Dashboard Content */}
          <main className="flex-1 overflow-auto p-6">
            <div className="max-w-7xl mx-auto space-y-8">
              {/* Statistics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <Card
                  className={`${
                    theme === "dark" ? "bg-slate-900/50 border-slate-700/50" : "bg-white/50 border-slate-200/50"
                  } backdrop-blur-sm`}
                >
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle
                      className={`text-sm font-medium ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`}
                    >
                      Total Locks
                    </CardTitle>
                    <Lock className={`h-4 w-4 ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`} />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${theme === "dark" ? "text-white" : "text-slate-900"}`}>
                      {fileLocks.length}
                    </div>
                  </CardContent>
                </Card>

                <Card
                  className={`${
                    theme === "dark" ? "bg-slate-900/50 border-slate-700/50" : "bg-white/50 border-slate-200/50"
                  } backdrop-blur-sm`}
                >
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle
                      className={`text-sm font-medium ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`}
                    >
                      Active Users
                    </CardTitle>
                    <Users className={`h-4 w-4 ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`} />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${theme === "dark" ? "text-white" : "text-slate-900"}`}>
                      {new Set(fileLocks.map((lock) => lock.user)).size}
                    </div>
                  </CardContent>
                </Card>

                <Card
                  className={`${
                    theme === "dark" ? "bg-slate-900/50 border-slate-700/50" : "bg-white/50 border-slate-200/50"
                  } backdrop-blur-sm`}
                >
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle
                      className={`text-sm font-medium ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`}
                    >
                      Computers
                    </CardTitle>
                    <Monitor className={`h-4 w-4 ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`} />
                  </CardHeader>
                  <CardContent>
                    <div className={`text-2xl font-bold ${theme === "dark" ? "text-white" : "text-slate-900"}`}>
                      {new Set(fileLocks.map((lock) => lock.computer)).size}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Search and Actions */}
              <div className="flex items-center justify-between gap-4">
                <div className="relative flex-1 max-w-md">
                  <Search
                    className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${
                      theme === "dark" ? "text-slate-400" : "text-slate-500"
                    }`}
                  />
                  <Input
                    placeholder="Search file locks..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className={`pl-10 ${
                      theme === "dark"
                        ? "bg-slate-900/50 border-slate-700/50 text-white placeholder:text-slate-400"
                        : "bg-white/50 border-slate-200/50 text-slate-900 placeholder:text-slate-500"
                    } backdrop-blur-sm`}
                  />
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRefresh}
                    className={`${
                      theme === "dark"
                        ? "text-slate-400 hover:text-slate-200 border-slate-600/50 hover:bg-slate-800/50"
                        : "text-slate-600 hover:text-slate-800 border-slate-300/50 hover:bg-slate-100/50"
                    } border backdrop-blur-sm`}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCleanup}
                    className={`${
                      theme === "dark"
                        ? "text-slate-400 hover:text-slate-200 border-slate-600/50 hover:bg-slate-800/50"
                        : "text-slate-600 hover:text-slate-800 border-slate-300/50 hover:bg-slate-100/50"
                    } border backdrop-blur-sm`}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Cleanup Stale Locks
                  </Button>
                </div>
              </div>

              {/* Active File Locks */}
              <Card
                className={`${
                  theme === "dark" ? "bg-slate-900/50 border-slate-700/50" : "bg-white/50 border-slate-200/50"
                } backdrop-blur-sm`}
              >
                <CardHeader>
                  <CardTitle
                    className={`text-xl font-bold tracking-wide bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent flex items-center gap-3`}
                  >
                    <Lock className="w-6 h-6 text-cyan-400" />
                    Active File Locks
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {filteredFileLocks.length === 0 ? (
                    <div className={`text-center py-8 ${theme === "dark" ? "text-slate-400" : "text-slate-600"}`}>
                      {searchQuery ? "No file locks match your search." : "No active file locks."}
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow className={`${theme === "dark" ? "border-slate-700/50" : "border-slate-200/50"}`}>
                          <TableHead className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                            File
                          </TableHead>
                          <TableHead className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                            User
                          </TableHead>
                          <TableHead className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                            Computer
                          </TableHead>
                          <TableHead className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                            Locked Since
                          </TableHead>
                          <TableHead className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"} px-4`}>
                            Actions
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredFileLocks.map((lock) => (
                          <TableRow
                            key={lock.id}
                            className={`${theme === "dark" ? "border-slate-700/50" : "border-slate-200/50"}`}
                          >
                            <TableCell className={`font-medium ${theme === "dark" ? "text-white" : "text-slate-900"}`}>
                              <div>
                                <div>{lock.file}</div>
                                <div className={`text-xs ${theme === "dark" ? "text-slate-400" : "text-slate-500"}`}>
                                  {lock.path}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                              <div>
                                <div>{lock.user}</div>
                                <div className={`text-xs ${theme === "dark" ? "text-slate-400" : "text-slate-500"}`}>
                                  PID: {lock.pid}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                              {lock.computer}
                            </TableCell>
                            <TableCell className={`${theme === "dark" ? "text-slate-300" : "text-slate-700"}`}>
                              {lock.lockedSince}
                            </TableCell>
                            <TableCell className="px-4">
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => handleRemoveLock(lock.id)}
                                className="bg-red-500 hover:bg-red-600 text-white"
                              >
                                Remove Lock
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}