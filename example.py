from pyclockify import ClockifyClient

if __name__ == "__main__":
    print("Input your API key:")
    api_key = input()
    client = ClockifyClient(api_key=api_key)
    workspaces = client.workspaces()
    print("List of all workspaces: ")
    print(
        *(
            f"* {w.name}:"
            + "\n projects:"
            + "".join(
                f"\n  * {p.name} hours: {p.duration.days * 24 + p.duration.seconds // 3600}"
                + "".join(
                    f"\n    * {t.name}: {t.status.name}" for t in client.tasks(w, p)
                )
                for p in client.projects(w)
            )
            + "\n Tags:"
            + "".join(f"\n  * {tag}" for tag in client.tags(w))
            + "\n Entries:"
            + "".join(f"\n  * {entry}" for entry in client.time_entries(w))
            + "\n Clients:"
            + "".join(f"\n  * {c}" for c in client.clients(w))
            for w in workspaces
        ),
        sep="\n",
    )
