import { getServerSession } from "next-auth/next";
import HydrationSafeDate from "@/components/HydrationSafeDate";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import Link from "next/link";
import { Globe, Calendar, Activity, Cpu } from "lucide-react";
import SignOutButton from "@/components/SignOutButton";
import prisma from "@/lib/prisma";

export default async function Home() {
  const session = await getServerSession(authOptions);

  if (!session || !session.user?.email) {
    redirect("/login");
  }

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
    include: {
      websites: {
        include: {
          content: {
            include: {
              jobs: {
                orderBy: { createdAt: 'desc' },
                take: 5
              }
            }
          }
        }
      }
    }
  });

  if (!user) {
    redirect("/login");
  }

  const websiteCount = user.websites.length;
  const contentItems = user.websites.flatMap((w) => w.content);
  const scheduledCount = contentItems.filter((i) => i.status === 'SCHEDULED').length;
  const publishedCount = contentItems.filter((i) => i.status === 'PUBLISHED').length;
  const recentJobs = user.websites
    .flatMap((w) => w.content.flatMap((c) => c.jobs))
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    .slice(0, 5);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <nav className="bg-white border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="bg-indigo-600 p-1.5 rounded-lg">
                <Cpu className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight">Content<span className="text-indigo-600">AI</span></span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-500">Welcome, {session.user?.name}</span>
              <Link href="/settings" className="text-sm font-medium text-gray-700 hover:text-indigo-600">Settings</Link>
              <SignOutButton />
            </div>
          </div>
        </div>
      </nav>

      <main className="py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {!user.googleApiKey && (
            <div className="mb-8 p-4 rounded-xl bg-red-50 border border-red-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Activity className="h-5 w-5 text-red-600" />
                <div>
                  <h4 className="text-sm font-semibold text-red-900">Google API Key Missing</h4>
                  <p className="text-sm text-red-800">You need to set your Google Gemini API key to use AI agents.</p>
                </div>
              </div>
              <Link href="/settings" className="text-sm font-bold text-red-700 hover:underline">Set API Key &rarr;</Link>
            </div>
          )}
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-2 text-sm text-gray-600">Overview of your autonomous content marketing empire.</p>
          </header>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {[
              { label: 'Connected Sites', value: websiteCount, icon: Globe, color: 'text-blue-600', bg: 'bg-blue-50' },
              { label: 'Scheduled Posts', value: scheduledCount, icon: Calendar, color: 'text-orange-600', bg: 'bg-orange-50' },
              { label: 'Published Posts', value: publishedCount, icon: Activity, color: 'text-green-600', bg: 'bg-green-50' },
              { label: 'Running Jobs', value: recentJobs.filter(j => j.status === 'RUNNING').length, icon: Cpu, color: 'text-indigo-600', bg: 'bg-indigo-50' },
            ].map((stat) => (
              <div key={stat.label} className="overflow-hidden rounded-xl bg-white p-5 shadow-sm border border-gray-100">
                <div className="flex items-center gap-4">
                  <div className={`${stat.bg} ${stat.color} p-3 rounded-lg`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {/* Quick Actions */}
            <div className="lg:col-span-2 space-y-8">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div className="overflow-hidden rounded-xl bg-white shadow-sm border border-gray-100 hover:border-indigo-300 transition-colors">
                  <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900">Manage Websites</h3>
                    <p className="mt-2 text-sm text-gray-500">Connect your WordPress sites to automate content generation and publishing.</p>
                    <div className="mt-6">
                      <Link href="/websites" className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 w-full">
                        View Sites
                      </Link>
                    </div>
                  </div>
                </div>

                <div className="overflow-hidden rounded-xl bg-white shadow-sm border border-gray-100 hover:border-indigo-300 transition-colors">
                  <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900">Content Calendar</h3>
                    <p className="mt-2 text-sm text-gray-500">Plan your strategy and watch the AI agents execute your content pipeline.</p>
                    <div className="mt-6">
                      <Link href="/calendar" className="inline-flex items-center justify-center rounded-lg bg-white border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 w-full">
                        Open Calendar
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="overflow-hidden rounded-xl bg-white shadow-sm border border-gray-100">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                <div className="flow-root">
                  <ul role="list" className="-mb-8">
                    {recentJobs.length === 0 && <p className="text-sm text-gray-500 italic">No recent activity found.</p>}
                    {recentJobs.map((job, idx) => (
                      <li key={job.id}>
                        <div className="relative pb-8">
                          {idx !== recentJobs.length - 1 ? (
                            <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-100" aria-hidden="true" />
                          ) : null}
                          <div className="relative flex space-x-3">
                            <div>
                              <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${job.status === 'COMPLETED' ? 'bg-green-500' :
                                job.status === 'RUNNING' ? 'bg-indigo-500' : 'bg-red-500'
                                }`}>
                                <Cpu className="h-4 w-4 text-white" />
                              </span>
                            </div>
                            <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                              <div>
                                <p className="text-sm text-gray-500">
                                  Agent job {job.status.toLowerCase()}{' '}
                                  <span className="font-medium text-gray-900">for scheduled post</span>
                                </p>
                              </div>
                              <div className="whitespace-nowrap text-right text-xs text-gray-500">
                                <HydrationSafeDate date={job.createdAt} mode="time" options={{ hour: '2-digit', minute: '2-digit' }} />
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-6">
                    <Link href="/calendar" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                      View all tasks &rarr;
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
