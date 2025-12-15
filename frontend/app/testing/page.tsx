"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Plus,
  FlaskConical,
  Calendar,
  Trash2,
} from "lucide-react";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import AppLayout from "../components/AppLayout";
import { useAuth } from "../../hooks/useAuth";
import {
  useProjects,
  useCreateProject,
  useDeleteProject,
  type Project,
} from "../../lib/api/testing";
import {
  createProjectSchema,
  type CreateProjectInput,
} from "../../lib/schemas/project";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
} from "../components/ui/dialog";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";

export default function TestingPage() {
  const router = useRouter();
  const { canCreateProject, canDeleteProject } = useAuth();

  // TanStack Query hooks
  const { data: projects = [], isLoading } = useProjects();
  const createMutation = useCreateProject();
  const deleteMutation = useDeleteProject();

  // Modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{
    id: string;
    name: string;
  } | null>(null);

  // React Hook Form for create project
  const form = useForm<CreateProjectInput>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
    },
  });

  const handleCreateProject = async (data: CreateProjectInput) => {
    try {
      await createMutation.mutateAsync(data);
      setShowCreateModal(false);
      form.reset();
    } catch (error) {
      console.error("Failed to create project", error);
    }
  };

  const confirmDeleteProject = (
    e: React.MouseEvent,
    id: string,
    name: string
  ) => {
    e.stopPropagation();
    e.preventDefault();
    setDeleteTarget({ id, name });
    setShowDeleteModal(true);
  };

  const executeDeleteProject = async () => {
    if (!deleteTarget) return;
    try {
      await deleteMutation.mutateAsync(deleteTarget.id);
    } catch (error) {
      console.error("Failed to delete", error);
    } finally {
      setShowDeleteModal(false);
      setDeleteTarget(null);
    }
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-hidden">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
              <FlaskConical className="w-6 h-6 text-indigo-600" />
              Testing
            </h1>
            <p className="text-slate-500 mt-1 text-sm">
              Automatisierte Testplan-Erstellung aus DDDs
            </p>
          </div>
          {canCreateProject && (
            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="w-5 h-5" />
              Neues Projekt
            </Button>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64 text-slate-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mr-3"></div>
            Lade Projekte...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6 overflow-y-auto pb-10">
            {projects.map((project: Project) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                onClick={() => router.push(`/testing/${project.id}`)}
                className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 cursor-pointer hover:shadow-xl hover:border-indigo-100 transition-all group relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                  {canDeleteProject && (
                    <button
                      onClick={(e) =>
                        confirmDeleteProject(e, project.id, project.name)
                      }
                      className="p-2 bg-white/80 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-lg backdrop-blur-sm transition-colors"
                      title="Projekt löschen"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-indigo-50 rounded-xl group-hover:bg-indigo-100 transition-colors">
                    <FlaskConical className="w-6 h-6 text-indigo-600" />
                  </div>
                </div>

                <h3 className="font-bold text-lg text-slate-900 mb-2 group-hover:text-indigo-600 transition-colors">
                  {project.name}
                </h3>

                <p className="text-slate-500 text-sm mb-6 line-clamp-2 h-10 leading-relaxed">
                  {project.description || "Keine Beschreibung"}
                </p>

                <div className="flex items-center text-xs font-medium text-slate-400 pt-4 border-t border-slate-50">
                  <Calendar className="w-3.5 h-3.5 mr-1.5" />
                  {new Date(project.created_at).toLocaleDateString()}
                </div>
              </motion.div>
            ))}

            {projects.length === 0 && (
              <div className="col-span-full items-center justify-center flex flex-col py-24 bg-white rounded-2xl border border-dashed border-slate-200">
                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                  <FlaskConical className="w-8 h-8 text-slate-300" />
                </div>
                <h3 className="text-slate-900 font-medium mb-1">
                  Keine Projekte
                </h3>
                <p className="text-slate-500 text-sm">
                  Erstelle ein neues Projekt um zu starten.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Create Modal with Radix Dialog */}
        <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
          <DialogContent>
            <form onSubmit={form.handleSubmit(handleCreateProject)}>
              <DialogHeader>
                <DialogTitle>Neues Projekt</DialogTitle>
              </DialogHeader>
              <div className="p-6 pt-2 space-y-4">
                <div>
                  <Label htmlFor="name">Projektname</Label>
                  <Input
                    id="name"
                    placeholder="z.B. Payment Service Update"
                    {...form.register("name")}
                    autoFocus
                  />
                  {form.formState.errors.name && (
                    <p className="text-red-500 text-sm mt-1">
                      {form.formState.errors.name.message}
                    </p>
                  )}
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setShowCreateModal(false)}
                >
                  Abbrechen
                </Button>
                <Button
                  type="submit"
                  isLoading={createMutation.isPending}
                  disabled={!form.formState.isValid}
                >
                  Projekt erstellen
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Modal */}
        <Dialog
          open={showDeleteModal}
          onOpenChange={(open) => {
            setShowDeleteModal(open);
            if (!open) setDeleteTarget(null);
          }}
        >
          <DialogContent>
            <DialogHeader>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <DialogTitle>Projekt löschen?</DialogTitle>
                  <p className="text-sm text-slate-500">
                    Diese Aktion kann nicht rückgängig gemacht werden.
                  </p>
                </div>
              </div>
            </DialogHeader>
            <div className="px-6 pb-2">
              <div className="bg-slate-50 rounded-xl p-4">
                <p className="text-sm font-medium text-slate-700 truncate">
                  {deleteTarget?.name}
                </p>
                <p className="text-xs text-slate-500">
                  Projekt und alle zugehörigen Daten werden gelöscht
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteTarget(null);
                }}
              >
                Abbrechen
              </Button>
              <Button
                onClick={executeDeleteProject}
                isLoading={deleteMutation.isPending}
                className="bg-red-600 hover:bg-red-700"
              >
                Löschen
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
